# Twitter Sentiment Analysis

### Project Overview
Great companies strive to provide outstanding customer satisfaction like it's an additional product or service. Understanding the market's opinion about your business or brand name is extremely valuable to decision makers, but getting that information can be expensive and hard. Luckily for us, 330 million people around the world are already using Twitter to talk about their experiences.

Tweet & Eat takes advantage of this fact to deliver an easy way for companies to guage consumer sentiment toward their brand or product based on what people are tweeting about it.

### How It Works
The user searches for a business name and city name located in Colorado. If a matching business is found in our database, the search term entered by the user is used to retrieve tweets containing that term from Twitter's API. A sentiment score between 1-5 is returned to the user along with one positive and negative tweet used during the analysis.

For optimal results:
- Narrow search to only keywords.
- Avoid apostrophes and other puncutaion.
- Example: Instead of searching for "The Cheesecake Factory" try "Cheesecake Factory".

### Analysis
Sentiment is determined using Machine Learning and Natural Language Processing. One hundred of the latest tweets containing the keyword search term are retrieved from Twitter's API before our algorithm assigns a classification label (positive or negative) to each one.

A "sentiment score" between 1-5 is determined based on the number of positive vs. negative tweets. The model was built using Python and the Natural Language ToolKit library. You can explore our algorithm's source code and a detailed use case here.

Access to larger Twitter datasets during each API request requires a paid Twitter developer account. This would greatly increase the accuracy of our sentiment score as well as allow us to conduct more in-depth analysis. We have opted to continue without signing up for a premium account until the app is production ready.

### Data Sources
Raw tweet data is collected from Twitter's API at the time of user interaction. Real-time access to twitter's database allows us to calculate consumer sentiment toward any given keyword(s) and supply the latest information. All business data is housed in our database. This information was collected using various web scraping techinques and API's.

### What I would do to improve
1) Analyze each tweet for the user's intent.
    * This can provide actionable insight and help business owners understand how their customers are interacting with their products and services. 
2) Analyze larger amounts of tweets.
    * Twiter restricts the number of returned tweets to 100 per API request when using a standard developer account.
    * Upgrading to premium or enterprise account is required to access more tweets per request.
3) Lemmatize words like 'hi' and 'hiiii'.
4) Detect sarcasm in tweets.

### References
1) Training the NaiveBayesClassifier - https://www.digitalocean.com/community/tutorials/how-to-perform-sentiment-analysis-in-python-3-using-the-natural-language-toolkit-nltk#step-1-%E2%80%94-installing-nltk-and-downloading-the-data

### Image Samples:
![Homepage](https://github.com/loganbonsignore/twitter-sentiment-analysis/blob/master/Images/homepage.png?raw=true)
![Database Overview](https://github.com/loganbonsignore/twitter-sentiment-analysis/blob/master/Images/database.png?raw=true)

![Search Result 1](https://github.com/loganbonsignore/twitter-sentiment-analysis/blob/master/Images/search_1.png?raw=true)

![Search Result 2](https://github.com/loganbonsignore/twitter-sentiment-analysis/blob/master/Images/search_2.png?raw=true)

![Analytical Value](https://github.com/loganbonsignore/twitter-sentiment-analysis/blob/master/Images/value.png?raw=true)