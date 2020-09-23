def top_tweet():
    import pandas as pd
    import pymongo
    
    conn="mongodb://localhost:27017"
    client = pymongo.MongoClient(conn)
    
    db = client.twitter_db
    
    # creating dataframe from db
    df = pd.DataFrame(list(db.cheesecake_factory.find()))

    # calculating total engagement
    df['total_engagement']=df[['num_of_favorites', 'num_of_replies', 'num_retweets']].sum(axis=1)

    # Finding the top 10 tweets based on total engagement
    top_tweets_df = df.sort_values("total_engagement", ascending=False).head(10)

    # assigning variables
    top_10_tweets = [tweet["original_tweet"] for index, tweet in top_tweets_df.iterrows()]
    top_tweet = top_tweets_df.iloc[0]["original_tweet"]
    
    return top_tweet, top_10_tweets