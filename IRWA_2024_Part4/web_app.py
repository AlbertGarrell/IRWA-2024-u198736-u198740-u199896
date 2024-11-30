import os
from json import JSONEncoder
import uuid

# pip install httpagentparser
import httpagentparser  # for getting the user agent as json
import nltk
from flask import Flask, render_template, session
from flask import request

from myapp.analytics.analytics_data import AnalyticsData, ClickedDoc
from myapp.search.load_corpus import load_corpus,load_processed_corpus
from myapp.search.objects import Document, StatsDocument
from myapp.search.search_engine import SearchEngine
from myapp.search.algorithms import create_tfidf,create_index
from datetime import datetime

# *** for using method to_json in objects ***
def _default(self, obj):
    return getattr(obj.__class__, "to_json", _default.default)(obj)

def format_date(value):
    try:
        return datetime.fromisoformat(value).strftime('%Y-%m-%d')
    except ValueError:
        return value  # Return as-is if parsing fails


_default.default = JSONEncoder().default
JSONEncoder.default = _default

# end lines ***for using method to_json in objects ***

# instantiate the Flask application
app = Flask(__name__)

app.jinja_env.filters['zip'] = zip

# Add the custom filter to Jinja2
app.jinja_env.filters['format_date'] = format_date

# random 'secret_key' is used for persisting data in secure cookie
app.secret_key = 'afgsreg86sr897b6st8b76va8er76fcs6g8d7'
# open browser dev tool to see the cookies
app.session_cookie_name = 'IRWA_SEARCH_ENGINE'

# instantiate our search engine
search_engine = SearchEngine()
# instantiate our in memory persistence
analytics_data = AnalyticsData()

@app.after_request
def log_http_response(response):
    """
    Logs HTTP request and response metadata after the response is processed.
    """
    ip = request.remote_addr
    http_method = request.method
    requested_url = request.url
    http_version = request.environ.get('SERVER_PROTOCOL', 'HTTP/1.1')
    response_status = response.status_code

    analytics_data.save_http_log(ip, http_method, requested_url, http_version, response_status)

    return response

# Home URL "/"
@app.route('/')
def index():
    print("starting home url /...")

    # flask server creates a session by persisting a cookie in the user's browser.
    # the 'session' object keeps data between multiple requests
    session['some_var'] = "IRWA 2021 home"

    user_agent = request.headers.get('User-Agent')

    print("Raw user browser:", user_agent)

    user_ip = request.remote_addr
    agent = httpagentparser.detect(user_agent)
    session_id = session.get('session_id', str(uuid.uuid4()))
    session['session_id'] = session_id

    print("Remote IP: {} - JSON user browser {}".format(user_ip, agent))

    print(session)

    analytics_data.save_session_data(session_id, user_agent, user_ip, datetime.now())

    return render_template('index.html', page_title="Welcome",results_per_page = 10)


@app.route('/search', methods=['POST'])
def search_form_post():
    search_query = request.form['search-query']
    results_per_page = int(request.form['results_per_page'])
    timestamp = datetime.now()

    session['last_search_query'] = search_query

    session_id = session.get('session_id', None)
    if not session_id:
        session_id = str(uuid.uuid4())
        session['session_id'] = session_id

    analytics_data.save_query_terms(search_query, session_id, timestamp)

    results, usernames = search_engine.search(search_query)
    
    found_count = len(results)
    session['last_found_count'] = found_count

    print(session)

    return render_template('results.html', results_list=results[:results_per_page], page_title="Results", found_counter=found_count,results_per_page = results_per_page,query = search_query, usernames = usernames[:results_per_page])


@app.route('/doc_details', methods=['GET'])
def doc_details():
    # getting request parameters:
    # user = request.args.get('user')

    print("doc details session: ")
    print(session)

    res = session["some_var"]

    print("recovered var from session:", res)

    # get the query string parameters from request
    clicked_doc_id = request.args["id"]
    p1 = int(request.args["search_id"])  # transform to Integer
    p2 = int(request.args["param2"])  # transform to Integer
    print("click in id={}".format(clicked_doc_id))

    # store data in statistics table 1
    if clicked_doc_id in analytics_data.fact_clicks.keys():
        analytics_data.fact_clicks[clicked_doc_id] += 1
    else:
        analytics_data.fact_clicks[clicked_doc_id] = 1

    print("fact_clicks count for id={} is {}".format(clicked_doc_id, analytics_data.fact_clicks[clicked_doc_id]))

    return render_template('doc_details.html')


@app.route('/stats', methods=['GET'])
def stats():
    """
    Show simple statistics example. ### Replace with dashboard ###
    :return:
    """

    docs = []
    # ### Start replace with your code ###

    for doc_id in analytics_data.fact_clicks:
        row: Document = corpus[int(doc_id)]
        count = analytics_data.fact_clicks[doc_id]
        doc = StatsDocument(row.id, row.title, row.description, row.doc_date, row.url, count)
        docs.append(doc)

    # simulate sort by ranking
    docs.sort(key=lambda doc: doc.count, reverse=True)
    return render_template('stats.html', clicks_data=docs)
    # ### End replace with your code ###


@app.route('/dashboard', methods=['GET'])
def dashboard():
    visited_docs = []
    print(analytics_data.fact_clicks.keys())
    for doc_id in analytics_data.fact_clicks.keys():
        d: Document = corpus[int(doc_id)]
        doc = ClickedDoc(doc_id, d.description, analytics_data.fact_clicks[doc_id])
        visited_docs.append(doc)

    # simulate sort by ranking
    visited_docs.sort(key=lambda doc: doc.counter, reverse=True)

    for doc in visited_docs: print(doc)
    return render_template('dashboard.html', visited_docs=visited_docs)


@app.route('/sentiment')
def sentiment_form():
    return render_template('sentiment.html')


@app.route('/sentiment', methods=['POST'])
def sentiment_form_post():
    text = request.form['text']
    nltk.download('vader_lexicon')
    from nltk.sentiment.vader import SentimentIntensityAnalyzer
    sid = SentimentIntensityAnalyzer()
    score = ((sid.polarity_scores(str(text)))['compound'])
    return render_template('sentiment.html', score=score)


if __name__ == "__main__":
    app.run(port=8088, host="0.0.0.0", threaded=False, debug=True)
