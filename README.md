# Upload chunks from a Youtube Channel's videos to Arguflow

## Install

Install the Python packages

```sh
pip install -r ./requirements.txt
```

## Deploy an Arguflow instance and REDIS

[Follow the self-hosting guide here](https://docs.arguflow.ai/self_hosting)

The `script-redis` service in the Arguflow docker-compose is intended to be used with this. If you go that route your `REDIS_URL` env value will be something like `REDIS_URL=redis://:thisredispasswordisverysecureandcomplex@<server-ip-address>:6380`. You can also use managed REDIS with something like [Render](https://render.com). 

## Get the CHANNEL_ID for the youtube channel you want to get transcripts from

Find the URL of the channel you want to deploy Arguflow on top of then get the CHANNEL_ID with a tool like [Comment Picker](https://commentpicker.com/youtube-channel-id.php)

## Set your ENV's

They should look something like: 

```
CHANNEL_ID=UC0vBXGSyV14uvJ4hECDOl0Q
YOUTUBE_API_KEY=***************************************
REDIS_PASSWORD=thisredispasswordisverysecureandcomplex
REDIS_URL=redis://:thisredispasswordisverysecureandcomplex@localhost:6380
ARGUFLOW_API_URL=http://localhost:8090/api
ARGUFLOW_API_KEY=af-********************************
```

## Add all of the video id's to a REDIS queue 

`python ./upload.py`

## Get the raw transcripts of the videos, punctuate them, then upload to your Arguflow instance 

You should typically run at least 6 of `main.py` process in parallel. 

`python ./main.py`
