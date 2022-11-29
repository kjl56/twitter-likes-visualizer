import time
import json
import configparser
import pandas as pd
from requests_oauthlib import OAuth1Session

#read config
config = configparser.ConfigParser()
config.read('config.ini')

api_key = config['twitter']['api_key']
api_key_secret = config['twitter']['api_key_secret']

access_token = config['twitter']['access_token']
access_token_secret = config['twitter']['access_token_secret']

#authentication
auth = OAuth1Session(api_key, api_key_secret, access_token, access_token_secret)

#read liked tweets list from twitter data file
with open('like.js', encoding="utf-8") as likeData:
  likeDic = json.load(likeData)

likeDataFrame = pd.json_normalize(likeDic)

def grabQueuedTweets(id, auth):
  json_response = {}
  params = {"ids": id, "tweet.fields": "created_at,lang,attachments,public_metrics", "expansions": "author_id", "user.fields": "created_at,protected,verified,location,profile_image_url,public_metrics"}
  response = auth.get("https://api.twitter.com/2/tweets", params=params)
  if response.status_code != 200:
    raise Exception(
      "Request returned an error: {} {}".format(response.status_code, response.text)
    )
  print("Response code: {}".format(response.status_code))
  json_response.update(response.json())
  return json_response

#fetch full tweet info from twitter api
id = ''
tweetCount = 0
tweetsDataFrame = pd.DataFrame()
userDataFrame = pd.DataFrame()
errorsDataFrame = pd.DataFrame()
for tweet in likeDataFrame['like.tweetId']:
  if (tweetCount == 0):
    id += tweet
    tweetCount += 1
  else:
    if (tweetCount < 100): #set to 100 since that is max tweets that can be grabbed at once from twitter api
      id += ("," + tweet)
      tweetCount += 1
    else: 
      #grab all queued tweets from twitter api, add to dataframes
      json_response = grabQueuedTweets(id, auth)
      tweetsDataFrame = pd.concat([tweetsDataFrame, pd.json_normalize(json_response, 'data')], ignore_index=True)
      userDataFrame = pd.concat([userDataFrame, pd.json_normalize(json_response, ['includes', 'users'])], ignore_index=True)
      try:
        errorsDataFrame = pd.concat([errorsDataFrame, pd.json_normalize(json_response, 'errors')], ignore_index=True)
      except:
        print("no deleted tweets detected in this batch")

      #reset id to current queued tweet since it wasn't grabbed, set tweetCount to 1
      id = tweet
      tweetCount = 1
      time.sleep(1) #set to 101 secs to not go over the api's max limit per 15min interval (15min * 60sec/min = 900 sec / 9 api calls = 100 sec) 

#grab whatever tweets are remaining in id
json_response = grabQueuedTweets(id, auth)
tweetsDataFrame = pd.concat([tweetsDataFrame, pd.json_normalize(json_response, 'data')], ignore_index=True)
userDataFrame = pd.concat([userDataFrame, pd.json_normalize(json_response, ['includes', 'users'])], ignore_index=True)
try:
  errorsDataFrame = pd.concat([errorsDataFrame, pd.json_normalize(json_response, 'errors')], ignore_index=True)
except:
  print("no deleted tweets detected in this batch")

print("all tweets complete")
tweetsDataFrame.info()
userDataFrame.info()
errorsDataFrame.info()

tweetsDataFrame.to_json("expandedLikedTweetsData.js", orient='records', indent=4)
userDataFrame.to_json("expandedLikedUsersData.js", orient='records', indent=4)
errorsDataFrame.to_json("deletedLikedTweetsData.js", orient='records', indent=4)