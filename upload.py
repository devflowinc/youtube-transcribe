import requests
import redis
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.environ.get("API_KEY")
CHANNEL_ID = os.environ.get("CHANNEL_ID")
REDIS_URL = os.environ.get("REDIS_URL")

r = redis.StrictRedis.from_url(REDIS_URL, decode_responses=True)

playlist_id = requests.get(
    f"https://youtube.googleapis.com/youtube/v3/channels?part=snippet%2CcontentDetails%2Cstatistics&id={CHANNEL_ID}&key={API_KEY}"
).json()["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

# Make a request to the YouTube Data API
response = requests.get(
    f"https://youtube.googleapis.com/youtube/v3/playlistItems?part=snippet%2CcontentDetails%2Cstatus&maxResults=100&playlistId={playlist_id}&key={API_KEY}"
)

def handle_video(video):
    try:
        videoId = video["contentDetails"]["videoId"]
        videoTitle = video["snippet"]["title"]
        videoIdPlusTitle = f"{videoId}||{videoTitle}"

        if r.sismember("completed", videoIdPlusTitle):
            print(f"Completed {videoIdPlusTitle}")
            return
        if r.sismember("in-progress", videoIdPlusTitle):
            print(f"In progress {videoIdPlusTitle}")
            return
        
        print(f"Processing {videoIdPlusTitle}")
        r.sadd("in-progress", videoIdPlusTitle)

    except:
        print("Error handling video")

if response.status_code == 200:
    data = response.json()
    videos = data.get("items", [])
    for video in videos:
        handle_video(video)

while "nextPageToken" in response.json():
    nextPageToken = response.json()["nextPageToken"]
    response = requests.get(
        f"https://youtube.googleapis.com/youtube/v3/playlistItems?part=snippet%2CcontentDetails%2Cstatus&maxResults=100&pageToken={nextPageToken}&playlistId={playlist_id}&key={API_KEY}"
    )
    if response.status_code == 200:
        data = response.json()
        videos = data.get("items", [])
        for video in videos:
            handle_video(video)
    else:
        print(f"Error: {response.text}")
