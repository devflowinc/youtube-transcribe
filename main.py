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
            video.streams.filter(only_audio=True).first().download(
                filename="audio.mp4")
        )
        transcription = whisper_model.transcribe(audio_file, verbose=False)
        df = pd.DataFrame(transcription["segments"], columns=[
                          "start", "end", "text"])
        for start in range(0, len(df), 8):
            end = min(start + 8, len(df))
            chunk = df.iloc[start:end]
            text = chunk["text"].astype(str).str.cat(sep="")
            data = {
                "card_html": text,
                "link": video_url + f"&t={math.floor(chunk.iloc[0]['start'])}",
                "private": False,
                "metadata": {
                    "Title": video.title,
                    "Description": video.description,
                    "Thumbnail": video.thumbnail_url,
                    "Channel": video.author,
                    "Duration": video.length,
                    "Uploaded At": video.publish_date.strftime("%Y-%m-%d %H:%M:%S"),
                },
            }
            print(data)
            response = requests.post(
                "http://localhost:8090/api/card", json=json.dumps(data)
            )
            print(video_url + f"&t={math.floor(chunk.iloc(0)['start'])}")
            if response.status_code != 200:
                print(f"Error: {response.text}")
                r.set(
                    "Error: " + video_url +
                    f"&t={math.floor(chunk.iloc(0)['start'])}",
                    "Error",
                )
        r.delete(key)
    except Exception as e:
        print("Error: " + str(e))
        r.set("Error: " + video_url, "Error")
        continue
