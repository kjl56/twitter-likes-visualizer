import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

#read in the 3 json filesd from the other script
tweetsDataFrame = pd.read_json("expandedLikedTweetsData.js")
usersDataFrame = pd.read_json("expandedLikedUsersData.js")
deletedDataFrame = pd.read_json("deletedLikedTweetsData.js")

#tweetsDataFrame.info()
#usersDataFrame.info()
#deletedDataFrame.info()

uniqueUsers = usersDataFrame.drop_duplicates(subset=['id'])
#print('userdataframe rows: ' + str(usersDataFrame.id.size))
print('total unique users interacted with: ' + str(uniqueUsers.id.size))

#num of times interacted with each user
totalLikesPerUser = tweetsDataFrame["author_id"].value_counts()
fig, ax = plt.subplots()
topXUsers = 25 
topLikedUsers = totalLikesPerUser.head(topXUsers)
stem = plt.stem(topLikedUsers)
my_range = range(0, len(topLikedUsers))

matchedUsernames = list()
for id in totalLikesPerUser.keys():
  matchedUsernames.append(uniqueUsers[uniqueUsers["id"] == id].loc[:, "username"].values[0])

ax.set_xticks(ticks= my_range, labels=matchedUsernames[0:topXUsers], rotation=45, ha='right')

#create annotation object
userX = 0
for value in topLikedUsers:  
  annotation = ax.annotate(
    text='{:.0f}'.format(value),
    xy=(userX, value),
    xytext=(0, 6), #distance from x, y
    textcoords='offset points',
    ha='center'
  )
  userX += 1

plt.title('Top {} Most Liked Accounts'.format(topXUsers))

#user locations

#stats from deleted likes
sectionTypes = deletedDataFrame["section"]
totalErrors = sectionTypes.size
notFound = sectionTypes.value_counts()
successfullyFetched = len(tweetsDataFrame.index)
total = totalErrors+successfullyFetched
nums = [notFound["data"], (totalErrors - notFound["data"]), successfullyFetched]
names = 'deleted\n{} ({:.2f}%)'.format(nums[0], (nums[0]/total)*100), 'access denied\n{} ({:.2f}%)'.format(nums[1], (nums[1]/total)*100), 'fetched\n{} ({:.2f}%)'.format(nums[2], (nums[2]/total)*100)
colors = ['#101010', '#FF5733', '#239B56']

fig, ax = plt.subplots()
ax.set_title('Fetched Tweets')
plt.pie(nums, labels=names, labeldistance=1.15, colors=colors)

#time series like frequency
fig, ax = plt.subplots()
datesGroup = pd.DataFrame()
datesGroup["created_at"] = pd.to_datetime(tweetsDataFrame["created_at"])
datesGroup = datesGroup.groupby(datesGroup["created_at"].dt.date).size().reset_index()
datesGroup = datesGroup.sort_values("created_at")
datesGroup.rename({0:'dateCount'}, axis='columns', inplace=True)
datesGroup['7day_rolling_avg'] = datesGroup.dateCount.rolling(7).mean()
datesGroup['30day_rolling_avg'] = datesGroup.dateCount.rolling(30).mean()

ax.set_title("Likes Per Day")
dailyPlot = plt.plot(datesGroup["created_at"], datesGroup["dateCount"], label='Daily Likes', linestyle='-', marker='.')
#plt.plot(datesGroup["created_at"], datesGroup['7day_rolling_avg'], label='7 Day Rolling Avg')
thirtyDayPlot = plt.plot(datesGroup["created_at"], datesGroup['30day_rolling_avg'], label='30 Day Rolling Avg')
fullPlot = dailyPlot + thirtyDayPlot

#create annotation object
annotation = ax.annotate(
  text='',
  xy=(0, 0),
  xytext=(15, 15), #distance from x, y
  textcoords='offset points',
  bbox={'boxstyle': 'round', 'fc': 'w'},
  arrowprops={'arrowstyle': '->'}
)
annotation.set_visible(False)

#implement annotation hover event
def update_annotation(line, idx):
  posx, posy = [line.get_xdata()[idx], line.get_ydata()[idx]]
  annotation.xy = (posx, posy)
  text = f'{line.get_label()}: {posy:.2f}'
  annotation.set_text(text)
  annotation.get_bbox_patch().set_alpha(0.4)

def motion_hover(event):
  visibility = annotation.get_visible()
  if event.inaxes == ax:
    for line in fullPlot:
      cont, ind = line.contains(event)
      if cont:
        update_annotation(line, ind['ind'][0])
        annotation.set_visible(True)
        fig.canvas.draw_idle()
      else:
        if visibility:
          annotation.set_visible(False)
          fig.canvas.draw_idle()

fig.canvas.mpl_connect('motion_notify_event', motion_hover)

plt.grid(linestyle=':')
plt.legend()



plt.show()