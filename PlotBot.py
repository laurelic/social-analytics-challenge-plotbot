#import necessary modules and info
import tweepy
from datetime import datetime
import matplotlib.pyplot as plt
import tweepy
import time
import json

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
analyzer = SentimentIntensityAnalyzer()

from config import (consumer_key, 
                    consumer_secret, 
                    access_token, 
                    access_token_secret)

def PullTweets(user):
    """Pulls 500 most recent tweets for a specified twitter user and contains them in a list"""
    
    # Setup Tweepy API Authentication
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth, parser=tweepy.parsers.JSONParser())
    
    #set up a list containing the tweets
    tweet_texts = []
    
    #create a variable to store the oldest tweet id for the loop
    ot = None
    
    #loop through 25 pages (20 tweets per page) of tweets to acquire 500 tweets
    for x in range(25):
        tweets = api.user_timeline(user, max_id = ot)
    
        #loop through the tweets themselves
        for t in tweets:
            
            #run Vader analysis on the tweet
            tweet_texts.append(t['text'])
            
            # store the tweet id in the oldest tweet variable and subtract 1 to continue iteration
            ot = t['id'] - 1
            
    return tweet_texts

def ScoreTweets(tweet_list = []):
    """Runs VADER sentiment analysis on a list of tweest and enumerates them"""
    
    #create a list to store compound score values
    score_list = []
    
    #set up a counter along with a list to contain counter values
    c = 0
    tweets_ago = []
    
    #iterate over the tweets
    for tweet in tweet_list:
        
        #analyze the tweet and add compound score the list
        score_list.append(analyzer.polarity_scores(tweet)['compound'])
        
        #add to counter and add to list
        c -= 1
        tweets_ago.append(c)
    
    return tweets_ago, score_list   

def PlotTweets(user, timeline = [], analysis = [],):
    """Generates a line plot analyzing the polarity scores for the tweets previously pulled"""
    
    #set plot size
    plt.figure(figsize = (10, 6))
    
    #plot the values contained in lists
    plt.plot(timeline, analysis, linestyle=":", marker="o", c="darkseagreen", label=user)
    plt.grid(color="0.75", linestyle="-")
    leg = plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.25),
              fancybox=True, shadow=True, title="Tweets")
    plt.title(f"Tweet Sentiment for {user} as of {timestamp}")
    plt.xlabel("Tweets Ago")
    plt.ylabel("Tweet Polarity")
    
    #save the figure in order to pull later
    plt.savefig("Resources/Tweet_Scores.png", bbox_extra_artists=(leg,), bbox_inches='tight')

def TweetPlot(user, request):
    """Tweets out plotted sentiment analysis for a user"""
    
    #authorize tweepy
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth, parser=tweepy.parsers.JSONParser())
    
    #send the tweet
    api.update_with_media("Resources/Tweet_Scores.png", "New Tweet Analysis for %s (Thank you, %s!)" % (user, request))

def CheckTweets(search):
    """Checks user timeline to ensure no duplicates of analyses"""
    
    #authorize tweepy
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth, parser=tweepy.parsers.JSONParser())
    
    #pull the user timeline
    public_tweets = api.user_timeline(count=50)
    
    #set up a counter for how many times a substring appears in the timeline
    counter = 0
    
    #check the tweets to ensure the search term has not already been mentioned
    for tweet in public_tweets:
        
        if "New Tweet Analysis for " + search in tweet['text']:
            counter += 1
    #return the result
    if counter > 0:
        return True
    else:
        return False

#start the analysis
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, parser=tweepy.parsers.JSONParser())

#set up the user_name to search for mentions
target_term = "@partofthtworld"


while(True):
    
    # Search for recent tweets
    tweet_search = api.search(target_term, count=100, result_type="recent")

    #check for mentions
    for tweet in tweet_search['statuses']:
        
        #check if any of the tweets contain requests for sentiment analysis
        if "Analyze @" in tweet['text']:
            requester = "@" + tweet["user"]["screen_name"]
            search_user = "@" + tweet['entities']['user_mentions'][1]['screen_name']
    
            #check if the user has been analyzed before
            check = CheckTweets(search_user)

            #if the analysis has not been run in the last 20 tweets, then run the analysis
            if check == False:

                #create a timestamp of the analysis
                timestamp = datetime.now().strftime("%m/%d/%Y %H:%M")

                #pull the tweets for requested user
                tweets = PullTweets(search_user)
                print(f"Sourced tweets for {search_user} at {timestamp}")

                #perform sentiment analysis on the tweet the tweets
                scores = ScoreTweets(tweets)
                print("Sentiment analysis performed.")

                #create visualization of the tweet sentiment
                PlotTweets(search_user, scores[0], scores[1])
                print("Visualizing sentiment analysis.")

                #post the analysis
                TweetPlot(search_user, requester)
                print("Analysis posted!")

            #note that the analysis has already been run
            else:
                print(f"Analysis for {search_user} was posted recently.")
    
    #set a timer to check every 5 minutes
    print("Scan finished. Will check again in 5 minutes.")
    time.sleep(300)
            

