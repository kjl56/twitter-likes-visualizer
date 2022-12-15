# twitter-likes-visualizer
visualizes the data from your twitter likes using MatPlotLib  
requires a free Twitter Developer account

How To Use
1. Download your Twitter data from your account settings
2. Find the file 'like.js' and copy it into the same folder as the downloaded scripts
3. modify 'config.ini' to use your api keys and access tokens from your Twitter Developer account
4. use python to run 'liked_tweets_no_tweepy.py' (will download additional data from twitter servers, creating 3 new files)
5. use python to run 'likesVisualizer.py'
6. Enjoy!

NOTE: Twitter does not store (or at least provide access to) the exact time that users liked a particular tweet, so creation time of the liked tweets is used instead
