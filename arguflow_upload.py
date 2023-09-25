import redis
from pytube import YouTube, Channel
import whisper
import pandas as pd
import requests
import json
import math

# Connect to Redis
r = redis.Redis(host="localhost", port=6379, decode_responses=True)
whisper_model = whisper.load_model("tiny")
# Get all the keys
keys = r.keys()

# Print the keys
for key in keys:
    try:
        video_url = key[8:]  # @param {type:"string"}
        video = YouTube(video_url)
        audio_file = (
            video.streams.filter(only_audio=True).first().download(filename="audio.mp4")
        )
        transcription = whisper_model.transcribe(audio_file)
        df = pd.DataFrame(transcription["segments"], columns=["start", "end", "text"])
        for index, row in df.iterrows():
            data = {
                "card_html": row["text"],
                "link": video_url + f"&t={math.floor(row['start'])}",
                "private": False,
                "metadata": {
                    "Title": video.title,
                    "Description": video.description,
                    "Thumbnail": video.thumbnail_url,
                    "Channel": video.author,
                    "Duration": video.length,
                    "Uploaded At": video.publish_date,
                },
            }
            response = requests.post(
                "http://localhost:8090/api/card", json=json.dumps(data)
            )
            print(video_url + f"&t={math.floor(row['start'])}")
            if response.status_code != 200:
                print(f"Error: {response.text}")
                r.set("Error: " + video_url + f"&t={math.floor(row['start'])}", "Error")
        r.delete(key)
    except Exception as e:
        print("Error: " + str(e))
        r.set("Error: " + video_url, "Error")
        continue
