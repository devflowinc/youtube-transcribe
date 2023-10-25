import redis
from youtube_transcript_api import YouTubeTranscriptApi
from pytube import YouTube
import requests
import json
import math


# Connect to Redis
r = redis.Redis(host="localhost", port=6379, decode_responses=True)
# Get all the keys
keys = r.keys()

# Print the keys
for key in keys:
    try:
        video_url = key[8:]  # @param {type:"string"}
        print(video_url)
        transcript = YouTubeTranscriptApi.get_transcript(video_url)
        video_url_link = "https://www.youtube.com/watch?v=" + video_url
        info = YouTube(video_url_link)
        for start in range(0, len(transcript), 20):
            end = min(start + 20, len(transcript))
            chunk = transcript[start:end]
            text = " ".join([i["text"] for i in chunk])
            data = {
                "card_html": text,
                "link": video_url_link + f"&t={math.floor(chunk[0]['start'])}",
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
            print(data)
        #     response = requests.post(
        #         "http://localhost:8090/api/card", json=json.dumps(data)
        #     )
        #     print(video_url + f"&t={math.floor(chunk[0]['start'])}")
        #     if response.status_code != 200:
        #         print(f"Error: {response.text}")
        #     r.set(
        #         "Error: " + video_url + f"&t={math.floor(chunk[0]['start'])}",
        #         "Error",
        #     )
        # r.delete(key)
    except Exception as e:
        print("Error: " + str(e))
        # r.set("Error: " + video_url, "Error")
        continue
