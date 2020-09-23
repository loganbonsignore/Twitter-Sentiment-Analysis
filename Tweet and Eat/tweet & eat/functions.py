import pandas as pd
import matplotlib.pyplot as plt
import descartes
import geopandas as gpd
from shapely.geometry import Point, Polygon
import pymongo
import random
import tweepy
import json
from config import api_key, secret_api_key, access_token, secret_access_token
import re
from flask import render_template

def plot_map():
    client = pymongo.MongoClient("mongodb://localhost:27017")
    db = client.restaurant_db
    street_map = gpd.read_file("Colorado_ZIP_Code_Tabulation_Areas__ZCTA_-shp/Colorado_ZIP_Code_Tabulation_Areas__ZCTA_.shp")
    # getting restaurant data
    restaurants = db.yelp.find({'is_closed': False})
    names = [restaurant["restaurant_name"] for restaurant in restaurants if (int(restaurant["coordinates"]["latitude"])> 36.5)]
    restaurants = db.yelp.find({'is_closed': False})
    longs = [restaurant["coordinates"]["longitude"] for restaurant in restaurants if (int(restaurant["coordinates"]["latitude"])> 36.5)]
    restaurants = db.yelp.find({'is_closed': False})
    lats = [restaurant["coordinates"]["latitude"] for restaurant in restaurants if (int(restaurant["coordinates"]["latitude"])> 36.5)]
    # creating dataframe
    df = pd.DataFrame({
        "name":names,
        "longitude":longs,
        "latitude":lats
    })
    # plotting map
    crs = {"init":"epsg:4326"}
    geometry = [Point(xy) for xy in zip(df["longitude"], df["latitude"])]
    geo_df = gpd.GeoDataFrame(df, crs=crs, geometry=geometry)
    fig, ax = plt.subplots()
    street_map.plot(ax=ax)
    geo_df.plot(ax=ax, markersize=7, color="whitesmoke")
    plt.title("Colorado")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.tight_layout()
    plt.savefig("static/images/map_plot.png", transparent=True)

def featured_restaurant():
    client = pymongo.MongoClient("mongodb://localhost:27017")
    db = client.restaurant_db
    restaurants = db.yelp.find({"image_url":{"$ne":"N/A"}, "is_closed":False, "is_claimed":True})
    all_restaurants = []
    for i in range(5):
        restaurant_dict = {}
        index = random.randint(0, db.yelp.find({"image_url":{"$ne":"N/A"}, "is_closed":False, "is_claimed":True}).count())
        restaurant_dict["name"] = restaurants[index]["restaurant_name"]
        restaurant_dict["img_url"] = restaurants[index]["image_url"]
        restaurant_dict["phone"] = restaurants[index]["restaurant_display_phone"]
        restaurant_dict["address"] = ", ".join(restaurants[index]["location"]["display_address"])
        all_restaurants.append(restaurant_dict)
    return all_restaurants

def data_table():
    client = pymongo.MongoClient("mongodb://localhost:27017")
    db = client.restaurant_db
    names = []
    phones = []
    categories = []
    prices = []
    addresses = []
    reviews = []
    for restaurant in db.yelp.find({"price":{"$ne":"N/A"},"reviews":{"$ne":"N/A"}, "is_closed": False, "is_claimed": True}):
        names.append(restaurant["restaurant_name"])
        phones.append(restaurant["restaurant_display_phone"])
        categories.append(restaurant["categories"][0]["title"])
        prices.append(restaurant["price"])
        addresses.append(", ".join(restaurant["location"]["display_address"]))
        reviews.append(restaurant["reviews"][0]["text"])

    df = pd.DataFrame({
        "Name":names,
        "Category":categories,
        "Price": prices,
        "Location": addresses,
        "Review": reviews
    })
    df = df.sample(frac=1).reset_index(drop=True).head(10)
    table = df.to_html(index=False, justify="center", classes="table table-striped bg-white")
    table = table.replace("\n","")
    
    return table

def get_tweets(search_term):
    auth = tweepy.OAuthHandler(api_key, secret_api_key)
    auth.set_access_token(access_token, secret_access_token)
    api = tweepy.API(auth)

    response = api.search(q=search_term,count=100,tweet_mode="extended",lang="en", result_type="mixed")

    if response:
        df = pd.DataFrame({
            "tweet_id":[i.id_str for i in response],
            "time_when_tweet_created":[i.created_at for i in response],
            "tweet_range":[i.display_text_range for i in response],
            "full_text":[i.full_text for i in response],
            "tweet_hastags":[i.entities["hashtags"] if i.place != None else None for i in response],
            "tweet_source":[i.source for i in response],
            "truncated":[i.truncated for i in response],
            "is_quoted_tweet_status":[i.is_quote_status for i in response],
            "retweet_count":[i.retweet_count for i in response],
            "favorite_count":[i.favorite_count for i in response],
            "user_name":[i.user.name for i in response],
            "screen_name":[i.user.screen_name for i in response]
        })

        return df
    
    else:
        return "N/A"

def search_by_name_city(name, city):
    client = pymongo.MongoClient("mongodb://localhost:27017")
    db = client.restaurant_db
    # normalize name for optimal search results
    name = name.lower()
    name = re.sub("\'(.*)", "", name)
    name = name.replace(" ","-")
    return_list = []
    for restaurant in db.yelp.find({"location.city":city}):
        if name in restaurant["alias"]:
            return_list.append(restaurant)
    if len(return_list) == 0:
        return_list.append("N/A")
    return return_list

def search_by_name(name):
    client = pymongo.MongoClient("mongodb://localhost:27017")
    db = client.restaurant_db
    # normalize name for optimal search results
    name = name.lower()
    name = re.sub("\'(.*)", "", name)
    name = name.replace(" ","-")
    return_list = []
    for restaurant in db.yelp.find():
        if name in restaurant["alias"]:
            return_list.append(restaurant)
    if len(return_list) == 0:
        return_list.append("N/A")
    return return_list

def convert_hours_to_table(time):
    if time[0] == "0":
        day_time = "am"
        hour = time[1]
        minutes = time[2:]
        converted_time = f"{hour}:{minutes}{day_time}"
    elif (time[:2] == "10") or (time[:2] == "11") or (time[:2] == "12"):
        day_time = "am"
        hour = time[:2]
        minutes = time[2:]
        converted_time = f"{str(hour)}:{minutes}{day_time}"
    elif time[0] != "0":
        day_time ="pm"
        minutes = time[2:]
        minutes = re.sub(":","",minutes)
        hour = time[:2]
        hour = re.sub(":","",hour)
        if int(hour) > 12:
            hour = int(hour) - 12
        converted_time = f"{str(hour)}:{minutes}{day_time}"
    else:
        converted_time = "N/A"
    
    return converted_time

def get_hours(hours):
    try:
        hours = hours[0]["open"]
    except:
        return "N/A"
    hours_list = []
    for hour in hours:
        return_dict = {}
        return_dict["start"] = (convert_hours_to_table(hour["start"]))
        return_dict["end"] = (convert_hours_to_table(hour["end"]))
        if hour["day"] == 0:
            return_dict["day"] = ("Sunday")
        elif hour["day"] == 1:
            return_dict["day"] = ("Monday")
        elif hour["day"] == 2:
            return_dict["day"] = ("Tuesday")
        elif hour["day"] == 3:
            return_dict["day"] = ("Wednesday")
        elif hour["day"] == 4:
            return_dict["day"] = ("Thursday")
        elif hour["day"] == 5:
            return_dict["day"] = ("Friday")
        elif hour["day"] == 6:
            return_dict["day"] = ("Saturday")
        else:
            return_dict["day"] = ("N/A")

        hours_list.append(return_dict)

    return hours_list

def convert_reviews(reviews):
    review_list = []
    for review in reviews:
        review_dict = {}
        review_dict["text"] = review["text"]
        date = review["time_created"]
        split = date.split(" ")
        date = split[0].split("-")
        date = f"{date[1]}/{date[2]}/{date[0]}"
        time = split[1].split(":")
        hour = time[0]
        minute = time[1]
        time = f"{hour}{minute}"
        time = convert_hours_to_table(time)
        review_dict["date"] = date
        review_dict["time"] = time
        review_dict["rating"] = review["rating"]
        review_dict["user_profile_image"] = review["user"]["image_url"]
        review_dict["user_name"] = review["user"]["name"]
        review_list.append(review_dict)

    return review_list

def get_matching_restaurant_data(matching_restaurant):
    client = pymongo.MongoClient("mongodb://localhost:27017")
    db = client.restaurant_db
    matching_restaurant_info = {}
    matching_restaurant_info["name"] = matching_restaurant["restaurant_name"]
    matching_restaurant_info["img_url"] = matching_restaurant["image_url"]
    matching_restaurant_info["phone"] = matching_restaurant["restaurant_display_phone"]
    matching_restaurant_info["address"] = ", ".join(matching_restaurant["location"]["display_address"])
    try:
        matching_restaurant_info["price"] = matching_restaurant["price"]
    except:
        matching_restaurant_info["price"] = "N/A"
    try:
        matching_restaurant_info["hours"] = matching_restaurant["hours"]
    except:
        matching_restaurant_info["hours"] = "N/A"
    try:
        matching_restaurant_info["picture_urls"] = [i for i in matching_restaurant["pictures"] if i != matching_restaurant_info["img_url"]]
    except:
        matching_restaurant_info["picture_urls"] = "N/A"
    try:
        matching_restaurant_info["categories"] = matching_restaurant["categories"][0]["title"]
    except:
        matching_restaurant_info["categories"] = "N/A"
    try:
        matching_restaurant_info["yelp_rating"] = matching_restaurant["rating"]
    except:
        matching_restaurant_info["yelp_rating"] = "N/A"
    try:
        matching_restaurant_info["reviews"] = matching_restaurant["reviews"]
    except:
        matching_restaurant_info["reviews"] = "N/A"
    try:
        matching_restaurant_info["coordinates"] = matching_restaurant["coordinates"]
    except:
        matching_restaurant_info["coordinates"] = "N/A"

    matching_zipcode = matching_restaurant["location"]["zip_code"]

    if matching_restaurant_info["hours"] != "N/A":
        hours_list = get_hours(matching_restaurant_info["hours"])
        if matching_restaurant_info["reviews"] != "N/A":
            reviews = convert_reviews(matching_restaurant_info["reviews"])
        else:
            reviews = "N/A"
        # Finding matching restaurants and putting them in for loop on page as recommendatations
        nearby_restaurants = db.yelp.find({"location.zip_code":matching_zipcode, "is_closed":False, "is_claimed":True})
        return matching_restaurant_info, hours_list, reviews, nearby_restaurants
    else:
        if matching_restaurant_info["reviews"] != "N/A":
            reviews = convert_reviews(matching_restaurant_info["reviews"])
        else:
            reviews = "N/A"
        nearby_restaurants = db.yelp.find({"location.zip_code":matching_zipcode, "is_closed":False, "is_claimed":True})
        hours_list = "N/A"
        return matching_restaurant_info, hours_list, reviews, nearby_restaurants

def analyze_tweets(df, classifier, clean_data, word_tokenize):
    client = pymongo.MongoClient("mongodb://localhost:27017")
    db = client.restaurant_db
    positive_count = 0
    negative_count = 0
    positive_tweets = []
    negative_tweets = []
    # analyzing tweets
    for index, row in df.iterrows():
        id_ = row["tweet_id"]
        search_id = f"https://twitter.com/x/status/{id_}"
        tweet = row["full_text"]
        date = row["time_when_tweet_created"]
        favorite_count = row["favorite_count"]
        user_name = row["user_name"]
        screen_name = row["screen_name"]
        tokens = clean_data(word_tokenize(tweet))
        result = classifier.classify(dict([token, True] for token in tokens))
        return_object = {
            "id":id_,
            "search_id":search_id,
            "tweet":tweet,
            "result":result,
            "date":date,
            "favorite_count":favorite_count,
            "user_name":user_name,
            "screen_name": screen_name
        }
        if return_object["result"] == "Negative":
            negative_count += 1
            negative_tweets.append(return_object)
            
        elif return_object["result"] == "Positive":
            positive_count += 1
            positive_tweets.append(return_object)
    
    if len(positive_tweets) < 10 or len(negative_tweets) < 10:
        sentiment_score = "N/A"
        positive_tweet = "N/A"
        negative_tweet = "N/A"
        positive_count = "N/A"
        negative_count = "N/A"
        return sentiment_score, positive_tweet, negative_tweet, positive_count, negative_count

    total_count = positive_count + negative_count
    sentiment_score = round((positive_count/total_count) * 5,2)
    try:
        pos_index = random.randint(0, len(positive_tweets))
        neg_index = random.randint(0, len(negative_tweets))
        positive_tweet = pd.DataFrame(list(positive_tweets)).iloc[pos_index]
        negative_tweet = pd.DataFrame(list(negative_tweets)).iloc[neg_index]
    except IndexError:
        positive_tweet = pd.DataFrame(list(positive_tweets)).iloc[0]
        negative_tweet = pd.DataFrame(list(negative_tweets)).iloc[0]

    return sentiment_score, positive_tweet, negative_tweet, positive_count, negative_count

def get_same_city_restuarants(search_city):
    client = pymongo.MongoClient("mongodb://localhost:27017")
    db = client.restaurant_db
    restaurants = db.yelp.find({"location.city":search_city, "is_closed":False,"is_claimed":True})
    try:
        check = restaurants[0]
        return restaurants
    except:
        return "N/A"

def get_same_name_restuarants(search_term):
    restaurants = search_by_name(search_term)
    try:
        check = restaurants[0]
        return restaurants
    except:
        restaurants = "N/A"
        return restaurants
