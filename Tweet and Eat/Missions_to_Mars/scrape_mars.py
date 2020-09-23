from splinter import Browser
from flask import Flask, jsonify, redirect
import pandas as pd
from bs4 import BeautifulSoup as bs
import time
import pymongo
import re
import datetime

def init_browser():
    executable_path = {"executable_path": "/usr/local/bin/chromedriver"}
    return Browser("chrome", **executable_path, headless=True)

def scrape():
    browser = init_browser()
    client = pymongo.MongoClient("mongodb://localhost:27017")
    db = client.mars_db
    
    # Retrieving news title and teaser
    browser.visit("https://mars.nasa.gov/news/")
    time.sleep(2)

    soup = bs(browser.html, "html.parser")
    items = soup.find("ul",class_="item_list")
    slides = items.find_all("li", class_="slide")

    news_titles = []
    news_paragraphs = []
    for slide in slides:
        news_title = slide.find("div", class_="content_title").text
        news_p = slide.find("div", class_="article_teaser_body").text
        news_titles.append(news_title)
        news_paragraphs.append(news_p)

    # Retrieving featured image url
    browser.visit("https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars")
    browser.find_by_id("full_image").click()
    time.sleep(2)

    soup = bs(browser.html, "html.parser")
    image_src = soup.find("img", class_="fancybox-image")["src"]

    featured_image_url = f"https://jpl.nasa.gov{image_src}"

    # Retriving mars facts table
    browser.visit("https://space-facts.com/mars/")
    df = pd.read_html(browser.html)[1]
    mars_facts_table_html = df.to_html(index=False, justify="center")
    mars_facts_table_html = mars_facts_table_html.replace("\n","")

    browser.visit("https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars")
    time.sleep(1)
    soup = bs(browser.html, "html.parser")

    # Retrieving hemishere page's urls
    hemisphere_urls = []
    hemispheres = soup.find_all("div", class_="description")
    for hemisphere in hemispheres:
        url = hemisphere.find("a")["href"]
        url = f"https://astrogeology.usgs.gov{url}"
        hemisphere_urls.append(url)

    # Retrieving titles and image links of different hemispheres
    hemisphere_list = []
    for hemisphere_url in hemisphere_urls:
        browser.visit(hemisphere_url)
        time.sleep(2)
        soup = bs(browser.html, "html.parser")
        title = soup.find("h2", class_="title").text
        title = re.sub(" Enhanced","",title)
        image_url = soup.find_all("li")[0].find("a")["href"]
        hemisphere_list.append({"title":title, "image_url":image_url})

    return_dict = {}
    return_dict["news_titles"] = news_titles
    return_dict["news_paragraphs"] = news_paragraphs
    return_dict["featured_image_url"] = featured_image_url
    return_dict["mars_facts_table_html"] = mars_facts_table_html
    return_dict["hemisphere_list"] = hemisphere_list
    return_dict["date"] = datetime.datetime.utcnow()
    
    db.mission_to_mars.update({}, return_dict, upsert=True)
    
    browser.quit()

    return return_dict