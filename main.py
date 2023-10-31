import redis
from youtube_transcript_api import YouTubeTranscriptApi
from pytube import YouTube
import math
from punctuators.models import PunctCapSegModelONNX

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

# Connect to Redis
r = redis.Redis(host="localhost", port=6379, decode_responses=True)
# Get all the keys
keys = r.keys()

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
            data = {
                "card_html": puncuated_text,
                "link": video_url + f"&t={math.floor(chunk[0]['start'])}",
                "private": False,
                "metadata": {
                    "Title": info.title,
                    "Description": info.description,
                    "Thumbnail": info.thumbnail_url,
                    "Channel": info.author,
                    "Duration": info.length,
                    "Uploaded At": info.publish_date.strftime("%Y-%m-%d %H:%M:%S"),
                },
            }
    except Exception as e:
        print("Error: " + str(e))

    video_data = pop_in_progress()