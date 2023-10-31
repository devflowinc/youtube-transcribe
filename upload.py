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

length = 0
total = 0

if response.status_code == 200:
    data = response.json()
    videos = data.get("items", [])
    for video in videos:
        total += 1
        r.set(
            f'Upload: https://www.youtube.com/watch?v={video["contentDetails"]["videoId"]}',
            video["snippet"]["title"],
        )
        print(total)


while "nextPageToken" in response.json():
    nextPageToken = response.json()["nextPageToken"]
    response = requests.get(
        f"https://youtube.googleapis.com/youtube/v3/playlistItems?part=snippet%2CcontentDetails%2Cstatus&maxResults=100&pageToken={nextPageToken}&playlistId={playlist_id}&key={API_KEY}"
    )
    if response.status_code == 200:
        data = response.json()
        videos = data.get("items", [])
        for video in videos:
            total += 1
            r.set(
                f'Upload: {video["contentDetails"]["videoId"]}',
                video["snippet"]["title"],
            )
            print(total)
    else:
        print(f"Error: {response.text}")
