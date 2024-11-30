import pandas as pd

from myapp.core.utils import load_json_file
from myapp.search.objects import Document

_corpus = {}


def load_processed_corpus(path):
    json_data = load_json_file(path)
    return json_data

def load_corpus(path) -> [Document]:
    """
    Load file and transform to dictionary with each document as an object for easier treatment when needed for displaying
     in results, stats, etc.
    :param path:
    :return:
    """
    df = _load_corpus_as_dataframe(path)
    df.apply(_row_to_doc_dict, axis=1)
    return _corpus


def _load_corpus_as_dataframe(path):
    """
    Load documents corpus from file in 'path'
    :return:
    """
    json_data = load_json_file(path)
    tweets_df = _load_tweets_as_dataframe(json_data)
    
    return tweets_df



def _load_tweets_as_dataframe(json_data):
    #  WE MAY NEED TO ADD USERNAME TOO (and more data maybe)
    # from index to column
    data = pd.DataFrame(json_data).transpose()
    data = data.reset_index()
    data.rename(columns={'index': 'id'}, inplace=True)
    return data

def _build_tags(row):
    tags = []
    # for ht in row["hashtags"]:
    #     tags.append(ht["text"])
    for ht in row:
        tags.append(ht["text"])
    return tags


def _build_url(row):
    url = ""
    try:
        url = row["entities"]["url"]["urls"][0]["url"]  # tweet URL
    except:
        try:
            url = row["retweeted_status"]["extended_tweet"]["entities"]["media"][0]["url"]  # Retweeted
        except:
            url = ""
    return url


def _clean_hashtags_and_urls(df):
    df["Hashtags"] = df["hashtags"].apply(_build_tags)
    df["Url"] = df.apply(lambda row: _build_url(row), axis=1)
    # df["Url"] = "TODO: get url from json"
    df.drop(columns=["entities"], axis=1, inplace=True)

def _row_to_doc_dict(row: pd.Series):
    _corpus[row['id']] = Document(row['id'], row['tweet'][0:100], row['tweet'], row['date'], row['likes'],
                                  row['retweets'],
                                  row['url'], row['hashtags'],row['comment_count'])

