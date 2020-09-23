from flask import Flask, render_template, redirect, jsonify
from flask_pymongo import PyMongo
import pandas as pd
import classifier
from functions import top_tweet

# Initiating server
app = Flask(__name__)

# Using PyMongo to connect with db
app.config["MONGO_URI"] = "mongodb://localhost:27017/twitter_db"
mongo = PyMongo(app)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/top_tweet")
def top_tweet():
    # creating dataframe from db
    df = pd.DataFrame(list(mongo.db.cheesecake_factory.find()))
    # calculating total engagement
    df['total_engagement']=df[['num_of_favorites', 'num_of_replies', 'num_retweets']].sum(axis=1)
    # Finding the top 10 tweets based on total engagement
    top_tweets_df = df.sort_values("total_engagement", ascending=False).head(11)
    # finding top tweet
    top_tweet_text = top_tweets_df.iloc[0]["original_tweet"]
    top_tweet_search_name = top_tweets_df.iloc[0]["search_term"].title()
    top_tweet_date_posted = top_tweets_df.iloc[0]["date_posted"]
    # finding other top tweets
    top_10_tweets = [tweet["original_tweet"] for index, tweet in top_tweets_df.iterrows() if tweet["original_tweet"] != top_tweet_text]

    return render_template("top_tweet.html", top_tweet_text=top_tweet_text, top_tweet_search_name=top_tweet_search_name, top_tweet_date_posted=top_tweet_date_posted, top_10_tweets=top_10_tweets)

if __name__ == "__main__":
    app.run(debug=True)

