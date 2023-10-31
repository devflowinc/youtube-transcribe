import redis
import requests
import json
from youtube_transcript_api import YouTubeTranscriptApi
from pytube import YouTube
import math
from punctuators.models import PunctCapSegModelONNX
import os
from dotenv import load_dotenv

load_dotenv()

ARGUFLOW_API_KEY = os.environ.get("ARGUFLOW_API_KEY")
ARGUFLOW_API_URL = os.environ.get("ARGUFLOW_API_URL")

class Card:
    def __init__(self, card_html, link, metadata_dict):
        self.card_html = card_html
        self.link = link
        self.metadata = metadata_dict
        if not self.metadata:
            print("Missing metadata.")
            exit(1)

    def to_json(self):
        def replace_nan_none(obj):
            if isinstance(obj, float) and (obj != obj or obj is None):
                return ""
            if obj is None:
                return ""
            if isinstance(obj, dict):
                return {key: replace_nan_none(value) for key, value in obj.items()}
            if isinstance(obj, list):
                return [replace_nan_none(item) for item in obj]
            return obj

        json_dict = {
            key: replace_nan_none(value) for key, value in self.__dict__.items()
        }

        return json.dumps(json_dict, sort_keys=True, default=str)

    def send_post_request(self):
        url = f"{ARGUFLOW_API_URL}/card"

        payload = self.to_json()

        headers = {"Content-Type": "application/json", "Authorization": ARGUFLOW_API_KEY}
        req_result = requests.post(url, data=payload, headers=headers)

        if req_result.status_code != 200:
            req_error = req_result.text
            print(req_error)

m: PunctCapSegModelONNX = PunctCapSegModelONNX.from_pretrained(
    "1-800-BAD-CODE/xlm-roberta_punctuation_fullstop_truecase"
)

def pop_in_progress():
    lua_script = """
    local item = redis.call('spop', KEYS[1])
    if item then
        redis.call('sadd', KEYS[2], item)
    end
    return item
    """

    keys = ["in-progress", "completed"]
    result = r.eval(lua_script, 2, *keys)
    return result

r = redis.Redis(host="localhost", port=6379, decode_responses=True)
r.ping()

video_data = pop_in_progress()
while video_data:
    video_id = video_data.split("||")[0]
    video_title = video_data.split("||")[1]
    video_url = f"https://www.youtube.com/watch?v={video_id}"

    print(f"Processing {video_id}||{video_title}")

    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id=video_id, languages=('en', 'en-US'))
        info = YouTube(video_url)
        for start in range(0, len(transcript), 30):
            end = min(start + 30, len(transcript))
            chunk = transcript[start:end]
            text = " ".join([i["text"] for i in chunk]).replace("\n", " ")
            puncuated_text = m.infer(texts=[text], apply_sbd=False)[0]
            metadata = {
                "Title": info.title,
                "Description": info.description,
                "Thumbnail": info.thumbnail_url,
                "Channel": info.author,
                "Duration": info.length,
                "Uploaded At": info.publish_date.strftime("%Y-%m-%d %H:%M:%S"),
            }
            link = video_url + f"&t={math.floor(chunk[0]['start'])}"
            card = Card(puncuated_text, link, metadata)
            card.send_post_request()
    except Exception as e:
        print("Error: " + str(e))

    video_data = pop_in_progress()