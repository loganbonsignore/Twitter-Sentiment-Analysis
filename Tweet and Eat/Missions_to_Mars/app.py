from flask import Flask, jsonify, render_template, redirect
import scrape_mars
import pymongo
from random import randint
from numpy import arange

app = Flask(__name__)
client = pymongo.MongoClient("mongodb://localhost:27017")
db = client.mars_db.mission_to_mars

@app.route("/")
def mars_data():                      
    mars_data = db.find().sort([("_id", -1)]).limit(1)[0]
    rand_int = randint(0,len(mars_data["news_titles"]))
    news = mars_data["news_titles"][rand_int]
    paragraphs = mars_data["news_paragraphs"][rand_int]

    return render_template("index.html", news_titles=news, \
        news_paragraphs=paragraphs, \
        featured_image_url=mars_data["featured_image_url"], \
        table=mars_data["mars_facts_table_html"], \
        hemisphere_list=mars_data["hemisphere_list"] 
    )

@app.route("/scrape")
def get_data():
    scrape_mars.scrape()
    
    return redirect("/", code=302)


if __name__ == "__main__":
    app.run(debug=True)