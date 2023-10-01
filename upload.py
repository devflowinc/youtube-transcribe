import requests
import redis

API_KEY = ""
CHANNEL_NAME = "lexfridman"
r = redis.Redis(host="localhost", port=6379, decode_responses=True)

playlist_id = requests.get(
    "https://youtube.googleapis.com/youtube/v3/channels",
    params={
        "part": "snippet,contentDetails,statistics",
        "forUsername": CHANNEL_NAME,
        "key": API_KEY,
    },
)
playlist_id.raise_for_status()
playlist_id = playlist_id.json()["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

total = 0
params = {
    "part": "snippet,contentDetails,status",
    "maxResults": 100,
    "playlistId": playlist_id,
    "key": API_KEY,
}
while True:
    response = requests.get("https://youtube.googleapis.com/youtube/v3/playlistItems", params=params)
    try:
        response.raise_for_status()
    except requests.exceptions.RequestException:
        print(f"Error: {response.text}")
        continue
    data = response.json()
    videos = data.get("items", [])
    for video in videos:
        total += 1
        r.set(
            f'Upload: https://www.youtube.com/watch?v={video["contentDetails"]["videoId"]}',
            video["snippet"]["title"],
        )
    if "nextPageToken" in data:
        params["pageToken"] = data["nextPageToken"]
    else:
        break
