from flask import Flask, jsonify, render_template, url_for, request, redirect
import random
import pymongo
import re, string
from nltk.tokenize import word_tokenize
from classifier import classifier, clean_data
import functions
import pandas as pd

# initiate app
app = Flask(__name__)

# connect to database
client = pymongo.MongoClient("mongodb://localhost:27017")
db = client.restaurant_db
functions.plot_map()

# define routes
@app.route("/")
def index():
    all_restaurants = functions.featured_restaurant()
    table = functions.data_table()
    return render_template("index.html", all_restaurants=all_restaurants, table=table)

@app.route("/result", methods=["GET", "POST"])
def review():
    try:
        if request.method == "POST":
            # get search value
            search_term = request.form["searchterm"].title()
            search_city = request.form["searchzip"].title()
            if not search_city and not search_term:
                search_city = "Denver"
                message = "Help us help you."
                same_city_restaurants = functions.get_same_city_restuarants(search_city)
                return render_template("error.html", same_city_restaurants=same_city_restaurants, city=search_city, message=message)
            elif not search_term and search_city:
                same_city_restaurants = functions.get_same_city_restuarants(search_city)
                if same_city_restaurants[0] != "N/A":
                    return render_template("city_only.html", same_city_restaurants=same_city_restaurants, city=search_city)
                else:
                    city = "Denver"
                    message = f"We couldn't find any matching businesses in {search_city}."
                    same_city_restaurants = functions.get_same_city_restuarants(city)
                    return render_template("error.html", same_city_restaurants=same_city_restaurants, city=search_city, message=message)
            elif search_term and not search_city:
                same_name_restaurants = functions.get_same_name_restuarants(search_term)
                if same_name_restaurants[0] != "N/A":
                    return render_template("name_only.html", same_name_restaurants=same_name_restaurants, term=search_term)
                else:
                    search_city = "Denver"
                    message = f"We couldn't find any businesses in our database that match {search_term}."
                    same_city_restaurants = functions.get_same_city_restuarants(search_city)
                    return render_template("error.html", same_city_restaurants=same_city_restaurants, city=search_city, message=message)
            else:
                # request twitter's API
                df = functions.get_tweets(search_term)
                if not isinstance(df, pd.DataFrame):
                    message = "Insufficient amount of tweets to calculate sentiment score. Try a new search term."
                    same_city_restaurants = functions.get_same_city_restuarants(search_city)
                    matching_restaurants = functions.search_by_name_city(search_term, search_city)
                    if matching_restaurants[0] != "N/A":
                        matching_restaurant_info, hours_list, reviews, nearby_restaurants = functions.get_matching_restaurant_data(matching_restaurants[0])
                        if hours_list == "N/A" and reviews == "N/A":
                            return render_template("result_not_enough_tweets_or_review_or_hours.html", searchterm=search_term, match=matching_restaurant_info, nearby_restaurants=nearby_restaurants, message=message)
                        elif hours_list == "N/A":
                            return render_template("result_not_enough_tweets_or_hours.html", searchterm=search_term, match=matching_restaurant_info, nearby_restaurants=nearby_restaurants, reviews=reviews, message=message)
                        elif reviews == "N/A":
                            return render_template("result_not_enough_tweets_or_reviews.html", searchterm=search_term, match=matching_restaurant_info, nearby_restaurants=nearby_restaurants, message=message, hours_table=hours_list)
                    else:
                        matching_restaurant_info, hours_list, reviews, nearby_restaurants = functions.get_matching_restaurant_data(matching_restaurants[0])
                        return render_template("result_not_enough_tweets.html", searchterm=search_term, match=matching_restaurant_info, nearby_restaurants=nearby_restaurants, hours_table=hours_list, reviews=reviews, message=message)
                # find matching restaurants in restaurant_db
                matching_restaurants = functions.search_by_name_city(search_term, search_city)
                # if matching restaurant is found, continue
                if matching_restaurants[0] != "N/A":
                    # getting matching restaurant info
                    matching_restaurant_info, hours_list, reviews, nearby_restaurants = functions.get_matching_restaurant_data(matching_restaurants[0])
                    if hours_list == "N/A":
                        sentiment_score, positive_tweet, negative_tweet, positive_count, negative_count = functions.analyze_tweets(df, classifier, clean_data, word_tokenize)
                        if sentiment_score == "N/A":
                            message = "Insufficient amount of tweets to calculate sentiment score. Try a new search term."
                            return render_template("result_not_enough_tweets.html", searchterm=search_term, match=matching_restaurant_info, nearby_restaurants=nearby_restaurants, hours_table=hours_list, reviews=reviews, message=message)
                        return render_template("result_no_hours.html", sentiment_score=sentiment_score, searchterm=search_term, positive_results=positive_count, negative_results=negative_count, positive_tweet=positive_tweet, negative_tweet=negative_tweet, match=matching_restaurant_info, nearby_restaurants=nearby_restaurants, reviews=reviews)
                    if reviews == "N/A":
                        sentiment_score, positive_tweet, negative_tweet, positive_count, negative_count = functions.analyze_tweets(df, classifier, clean_data, word_tokenize)
                        if sentiment_score == "N/A":
                            message = "Insufficient amount of tweets to calculate sentiment score. Try a new search term."
                            return render_template("result_not_enough_tweets.html", searchterm=search_term, match=matching_restaurant_info, nearby_restaurants=nearby_restaurants, hours_table=hours_list, reviews=reviews, message=message)
                        return render_template("result_no_reviews.html", sentiment_score=sentiment_score, searchterm=search_term, positive_results=positive_count, negative_results=negative_count, positive_tweet=positive_tweet, negative_tweet=negative_tweet, match=matching_restaurant_info, nearby_restaurants=nearby_restaurants, hours_table=hours_list)
                    else:
                        # analyzing tweets
                        sentiment_score, positive_tweet, negative_tweet, positive_count, negative_count = functions.analyze_tweets(df, classifier, clean_data, word_tokenize)
                        if sentiment_score == "N/A":
                            message = "Insufficient amount of tweets to calculate sentiment score. Try a new search term."
                            return render_template("result_not_enough_tweets.html", searchterm=search_term, match=matching_restaurant_info, nearby_restaurants=nearby_restaurants, hours_table=hours_list, reviews=reviews, message=message)
                        return render_template("result.html", sentiment_score=sentiment_score, searchterm=search_term, positive_results=positive_count, negative_results=negative_count, positive_tweet=positive_tweet, negative_tweet=negative_tweet, match=matching_restaurant_info, nearby_restaurants=nearby_restaurants, hours_table=hours_list, reviews=reviews)
                else:
                    same_city_restaurants = functions.get_same_city_restuarants(search_city)
                    return render_template("no_results.html", same_city_restaurants=same_city_restaurants, city=search_city, search_term=search_term)
        else:
            return redirect("/")
    except:
        search_city = "Denver"
        message=f"Something went wrong on our end. Please try another search term."
        same_city_restaurants = functions.get_same_city_restuarants(search_city)
        return render_template("error.html", same_city_restaurants=same_city_restaurants, city=search_city, message=message)

@app.route("/use_case")
def use_case():
    
    return render_template("use_case.html")

@app.route("/sentiment_analysis")
def sentiment_analysis():

    return render_template("sentiment_analysis.html")

if __name__ == "__main__":
    app.run(debug=True)