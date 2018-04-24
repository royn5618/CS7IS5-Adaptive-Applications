CS7IS5 : Adaptive Applications

Project 1: News Recommender System (newsrecoapp)
Project 2: Movie Recommender System (movierecoapp)



News Recommender System Instructions
==
Requires Django 1.11.11 or 2.0.x , Python 3.5, Textrazor and requests package to be installed.
News is fetched from newsapi.org for Ireland country.
TextRazor is used to do text analysis for keyword extraction.
TextRazor allows only 500 requests per day on free account.

To install TextRazor
--
* Type `pip install textrazor`

To test News Retrieval
--
Open the project in IDE and run the test. If using pycharm-
* Goto newsrecoapp/application/tests.py
* Right click on `class TestDataRetrieval(TestCase):`
* Select run.

To test Text Razor Keyword Extraction
--
Open the project in IDE and run the test. If using pycharm-
* Goto newsrecomapp/application/tests.py
* Right click on `class TestTextExtractor(TestCase):`
* Select run.


Inorder to run DJango server- 
--
* Goto terminal and in the directory adaptiveapp/newsrecomapp type
```
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

This should run the django server. You can access it on -
`localhost:8000`

To access models-
```
Browse to localhost:8000/admin
```

To run celery server to run periodic tasks you need to install Celery and Rabbit-MQ and then run:
```
/adaptiveapp/newsrecoapp$ celery -A newsrecoapp worker -B --loglevel=info
```
This will run the periodic_update_news() task in tasks.py, perform analysis and insert the news in table every 5 mins.

