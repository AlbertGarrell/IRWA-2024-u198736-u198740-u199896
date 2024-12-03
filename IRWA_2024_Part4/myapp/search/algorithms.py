from collections import defaultdict
from array import array
import math
import numpy as np

from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
import math
import collections
from numpy import linalg as la
import pandas as pd
import json
import re
import demoji
import time
from datetime import datetime, timezone
import math

def get_newest_date(tweets):
    """
    Finds the newest tweet based on the date.

    Input:
        tweets: dict - dictionary where keys are identifiers (e.g., "doc_0", "doc_1") 
                       and values are JSON-like objects with a 'date' field in ISO format.

    Output:
        newest_tweet: dict - the tweet JSON object with the most recent date.
    """
    # Convert dates and find the tweet with the maximum date
    newest_date = max(tweets.values(), key=lambda tweet: datetime.fromisoformat(tweet.get_date().replace("Z", "+00:00")))
    newest_date = newest_date.get_date()
    return  datetime.fromisoformat(newest_date.replace("Z", "+00:00"))


def build_terms(line):
    """
    Description:
    Preprocess the text (tweet) by removing stop words, punctuation (but keeping numbers), URLs,
    stemming, transforming to lowercase, and extracting hashtags. The hashtags are excluded
    from the preprocessed text.

    Input:
    line -- string (text) to be preprocessed

    Output:
    preprocessed_line -- a list of tokens corresponding to the input text after preprocessing
    hashtags -- a list of extracted hashtags
    """

    stemmer = PorterStemmer()
    stop_words = set(stopwords.words("english"))

    # Transform to lowercase
    line = line.lower()

    # HASHTAGS

    # Extract hashtags (keeping the # symbol)
    hashtags = re.findall(r'#\w+', line)
    # Remove punctuation but keep numbers
    hashtags = [re.sub(r'[^a-z0-9\s]', '', word) for word in hashtags]
    # Remove empty strings (in case stemming or other operations result in an empty hashtag)
    hashtags = [word for word in hashtags if word]

    # LINE

    # Remove emojis using demoji
    line = demoji.replace(line, " ")
    # Remove hashtags from the text --> remove all the word
    line = re.sub(r'#\w+', '', line)
    # Remove URLs
    line = re.sub(r'http\S+|www\S+|https\S+', '', line)
    # Remove punctuation but keep numbers (and hashtags are already removed)
    line = re.sub(r'[^a-z0-9\s]', '', line)
    # Tokenize the text to get a list of terms
    line = line.split()
    # Remove the word amp since & it is parsed as &amp and it is one of the most frequent words!
    line = [word for word in line if word != 'amp']
    # Remove stopwords
    line = [word for word in line if word not in stop_words]
    # Perform stemming
    line = [stemmer.stem(word) for word in line]

    # Return preprocessed text and hashtags
    return line, hashtags # return the preprocessed tweet content and hashtags 

def popularity_score(tweet,recent_date): # compute the popularity score defined above based on the tweet characteristics
    """
    Computes a popularity score based on tweets characteristics

    Input:
        tweet: tweet json object
        recent_date: date of the most recent tweet

    Output:
        Popularity Score (number)
    """
    likes = tweet.get_likes()
    retweets = tweet.get_retweets()
    comments = tweet.get_comment_count()
    date = tweet.get_date()
    date = datetime.fromisoformat(date.replace("Z", "+00:00"))


    # Calculate recency factor
    days_since_tweet = (recent_date - date).days
    recency_factor = math.exp(-0.05 * days_since_tweet)  # Decay factor based on days

    # Calculate popularity score
    score = (0.5 * likes + 0.5 * retweets + 0.3 * comments) * recency_factor

    return score

def rank_documents(query, docs, index,original_tweets_dict, tf, idf, recent_date):
    """
    Ranks documents based on their relevance (in descending order) to the query using TF-IDF scores.

    Input:
        query: The search query as a list of terms (preprocessed)
        docs: A list of document IDs to be ranked.
        index: The inverted index for tweets.
        processed_tweets: processed tweets dictionary
        original_tweets_dict: original tweets dictionary
        tf: term frequency dictionary
        idf: The inverse document frequency dictionary.
        alpha: Weight for the TF-IDF score.
        beta: Weight for the similarity score between hashtags.
        flag: boolean which indicates whether to use or not the hashtag similarity score (additional to the tf-idf)
        recent_date: date of the most recent tweet

    Output:
        A list of document IDs sorted by their relevance to the query and their scores
    """
    doc_vectors = defaultdict(lambda: [0] * len(query))  # Initialize all scores to 0
    query_vector = [0] * len(query)

    query_terms_count = collections.Counter(query)

    query_norm = la.norm(list(query_terms_count.values()))


    for termIndex, term in enumerate(query):
        if term not in index:
        # as the term does not exist, return anything
            return []

        query_vector[termIndex] = query_terms_count[term] / query_norm * idf[term]

        for doc_index, (doc, postings) in enumerate(index[term]):
            if doc in docs:
            #if doc in tf and term in tf[doc] and doc in tfidf and term in tfidf[doc]:
                doc_vectors[doc][termIndex] = tf[term][doc_index] * idf[term]

    # array d'arrays
    scores = [[np.dot(curDocVec, query_vector), doc] for doc, curDocVec in doc_vectors.items() ]

    # compute the similarity between query and hashtags --> we are joining query together as hashtags are one-word terms
    for doc_id in docs:
        
        for i in range(len(scores)):
            if scores[i][1] == doc_id:
                # for the popularity score
                temp = popularity_score(original_tweets_dict[doc_id],recent_date)
                scores[i][0] = scores[i][0] + temp

                break  # Exit the loop once the doc_id is found

    scores.sort(reverse=True)
    ranked_tweets = [x[1] for x in scores]


    # Sort documents by relevance score (descending)
    return ranked_tweets, scores

def search_in_corpus(query,corpus,index,tf,idf,newest_date):

    # process the query
    query_terms = build_terms(query)[0]
    docs = set(corpus.keys())
    flag = False
    for term in query_terms:
        try:
            # store in term_docs the ids of the docs that contain "term"
            term_docs=[posting[0] for posting in index[term]]

            # docs = docs Intersection term_docs --> applying AND method for tweets seach
            docs = docs.intersection(set(term_docs))
        except:
            #term is not in index
            pass
    
    docs = list(docs)
    try:
        ranked_tweets,scores = rank_documents(query_terms, docs, index,corpus, tf, idf,newest_date)
        return ranked_tweets
    except:
        return []

def create_index(tweets):
    """
    Description:
    Creates a full inverted index based on the content of the dictionary

    Input:
    tweets -- dictionary with 'tweet' variable that contains the processed tweet content.

    Output:
    full inverted index with all the corpus processed terms, documents where they appear and its corresponding positions
    """
    # init the dictionary
    index = defaultdict(list)

    for tweet_id, tweet_data in tweets.items():
        # get current tweet content (pre-processed)
        terms = tweet_data['tweet']
        # inverted index for current tweet
        current_tweet_index = defaultdict(lambda: [tweet_id, array('I')])  # defaultdict with list of positions
        #  Counts occurrences of each term in the tweet
        term_counts = defaultdict(int)

        # Build term frequency for this tweet and position lists
        for position, term in enumerate(terms):
            current_tweet_index[term][1].append(position)
            term_counts[term] += 1
        # Update index
        for term, (id, positions) in current_tweet_index.items():
            index[term].append([tweet_id, positions])
    return index

def create_tfidf(tweets, num_documents):
    """
    Optimized inverted index creation with TF, DF, and IDF calculations.

    Input:
    tweets -- doctionary of preprocessed tweets
    num_documents -- total number of tweets in the corpus

    Output:
    tf - normalized term frequency for each term in each document
    df - number of documents each term appear in
    idf - inverse document frequency of each term
    """

    tf = defaultdict(list)  # term frequencies of terms in documents
    df = defaultdict(int)    # document frequencies of terms in the corpus
    idf = {}

    for tweet_id, tweet_data in tweets.items():
        terms = tweet_data['tweet']
        current_tweet_index = defaultdict(lambda: [tweet_id, array('I')])  # defaultdict with list of positions
        term_counts = defaultdict(int)  # Counts occurrences of each term in the tweet

        # Build term frequency for this tweet and position lists
        for position, term in enumerate(terms):
            current_tweet_index[term][1].append(position)
            term_counts[term] += 1

        # Calculate L2 norm for the tweet (once per document)
        norm = math.sqrt(sum(count ** 2 for count in term_counts.values()))

        # Update index, TF, and DF
        for term, (id, positions) in current_tweet_index.items():
            # Normalized term frequency
            tf_value = term_counts[term] / norm
            tf[term].append(np.round(tf_value, 4))

            # Increment DF count (only once per document per term)
            df[term] += 1
    # Compute IDF for each term
    for term, doc_count in df.items():
        idf[term] = np.round(np.log(num_documents / doc_count), 4)

    return tf, df, idf

def get_usernames(docId_list):
    id_list = []
    id_maps = pd.read_csv('./data/tweet_document_ids_map.csv')
    
    for id in docId_list:
        id_list.append(id_maps.loc[id_maps['docId'] == id, 'id'].values[0])
    
    with open('./data/farmers-protest-tweets.json', 'r') as originals: 
        usernames = []
        for id in id_list:
            for line in originals:
                try:
                    tweet = json.loads(line)  # Load each line as a separate JSON object
                    if tweet['id'] in id_list:
                        usernames.append(tweet['user']['username'])
                except json.JSONDecodeError:
                    print("Skipping invalid JSON line.")
    return usernames

def process_date(results):
    for item in results:
        # Parse and reformat the date
        item.date = datetime.fromisoformat(item.date).strftime('%Y-%m-%d')
    return results

def get_tweet(doc_id,corpus):
    return corpus[doc_id]

