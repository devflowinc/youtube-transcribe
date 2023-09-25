import requests
import redis

API_KEY = "AIzaSyCB_Ce9iE8BPTA5JYKl6dIDCkJZOBxgjyg"
CHANNEL_NAME = "lexfridman"
r = redis.Redis(host="localhost", port=6379, decode_responses=True)

playlist_id = requests.get(
    f"https://youtube.googleapis.com/youtube/v3/channels?part=snippet%2CcontentDetails%2Cstatistics&forUsername={CHANNEL_NAME}&key={API_KEY}"
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
                f'Upload: https://www.youtube.com/watch?v={video["contentDetails"]["videoId"]}',
                video["snippet"]["title"],
            )
            print(total)
    else:
        print(f"Error: {response.text}")
