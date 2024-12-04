import os
from json import JSONEncoder
import uuid

# pip install httpagentparser
import httpagentparser  # for getting the user agent as json
import nltk
from flask import Flask, render_template, session
from flask import request
from flask import jsonify


from myapp.analytics.analytics_data import AnalyticsData, ClickedDoc
from myapp.search.load_corpus import load_corpus,load_processed_corpus
from myapp.search.objects import Document, StatsDocument
from myapp.search.search_engine import SearchEngine
from myapp.search.algorithms import create_tfidf,create_index,get_tweet
from datetime import datetime
import pandas as pd

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
    #ip = request.remote_addr
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
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


    session['last_search_query'] = search_query

    session_id = session.get('session_id', None)
    if not session_id:
        session_id = str(uuid.uuid4())
        session['session_id'] = session_id

    analytics_data.save_query_terms(search_query, session_id)

    results, usernames = search_engine.search(search_query)
    
    found_count = len(results)
    session['last_found_count'] = found_count

    print(session)

    return render_template('results.html', results_list=results[:results_per_page], page_title="Results", found_counter=found_count,results_per_page = results_per_page,query = search_query, usernames = usernames[:results_per_page])


@app.route('/clicked_doc', methods=['POST'])
def count_click():
    query = request.args.get('query')
    tweet_id = request.args.get('tweet_id')
    dwell_time = request.args.get('dwell_time')
    
    print(f"DocID: {tweet_id}")
    print(f"Query: {query}")
    print(f"Dwell_time: {dwell_time}")

    # save query and tweet id with its dwell time
    analytics_data.save_click(tweet_id, query, dwell_time=dwell_time)

    return '', 204 # ok status without data



@app.route('/stats', methods=['GET'])
def stats():
    """
    Show simple statistics example. ### Replace with dashboard ###
    :return:
    """

    docs = []

    file_path = "./data_storage/click_logs.csv"

    # Read the CSV file into a DataFrame
    clicks = pd.read_csv(file_path)

    for doc_id in clicks["doc_id"].unique():
        count = clicks[clicks["doc_id"]==doc_id].shape[0]
        mean_time = clicks[clicks["doc_id"]==doc_id]["dwell_time"].mean()
        max_time = clicks[clicks["doc_id"]==doc_id]["dwell_time"].max()
        min_time = clicks[clicks["doc_id"]==doc_id]["dwell_time"].min()
        total_queries = len(clicks[clicks["doc_id"]==doc_id]["query"].unique())
        full = get_tweet(doc_id, search_engine.corpus)

        obj = {
            "id": doc_id,
            "count": count,
            "mean_time": mean_time,
            "max_time": max_time,
            "min_time":  min_time,
            "total_queries": total_queries,
            "item": full
        }

        docs.append(obj)

    docs = sorted(docs, key=lambda x: x['count'], reverse=True)
    return render_template('stats.html',clicks_data = docs)
    


@app.route('/dashboard', methods=['GET'])
def dashboard():

    # get clicks per document ---------------------
    docs = []
    file_path = "./data_storage/click_logs.csv"
    # Read the CSV file into a DataFrame
    clicks = pd.read_csv(file_path)
    for doc_id in clicks["doc_id"].unique():
        count = clicks[clicks["doc_id"]==doc_id].shape[0]
        mean_time = clicks[clicks["doc_id"]==doc_id]["dwell_time"].mean()
        max_time = clicks[clicks["doc_id"]==doc_id]["dwell_time"].max()
        min_time = clicks[clicks["doc_id"]==doc_id]["dwell_time"].min()
        total_queries = len(clicks[clicks["doc_id"]==doc_id]["query"].unique())
        full = get_tweet(doc_id, search_engine.corpus)

        obj = {
            "id": doc_id,
            "count": count,
            "mean_time": mean_time,
            "max_time": max_time,
            "min_time":  min_time,
            "total_queries": total_queries,
            
        }

        docs.append(obj)

    docs = sorted(docs, key=lambda x: x['count'], reverse=True)
    # -----------------------------------------------

    # get user's dashboard data ---------------------

    browser_data = []

    file_path = "./data_storage/session_data.csv"
    # Read the CSV file into a DataFrame
    sessions = pd.read_csv(file_path)

    for browser in sessions["Browser"].unique():
        obj = {
            "browser": browser,
            "count": sessions[sessions["Browser"]==browser].shape[0]
        }
        browser_data.append(obj)
    
    op_systems = []
    for os in sessions["OS"].unique():
        obj = {
            "os": os,
            "count": sessions[sessions["OS"]==os].shape[0]
        }
        op_systems.append(obj)

    # -----------------------------------------------

    return render_template('dashboard.html', visited_docs=docs, browsers=browser_data,op_systems = op_systems)


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
