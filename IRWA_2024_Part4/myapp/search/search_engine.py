import random

from myapp.search.objects import ResultItem, Document
from myapp.search.algorithms import create_index,create_tfidf,search_in_corpus,get_newest_date, get_usernames, process_date
from myapp.search.load_corpus import load_corpus,load_processed_corpus


class SearchEngine:
    """educational search engine"""

    def __init__(self) -> None:
        self.corpus = None
        self.processed_corpus = None
        self.index = None
        self.tf = None
        self.idf = None
        self.df = None
        self.newest_date = None

        self.process()

    def search(self, search_query):
        #print("Search query:", search_query)
        results = search_in_corpus(search_query,self.corpus,self.index,self.tf,self.idf,self.newest_date)
        final_result = []
        for id in results:
            final_result.append(self.corpus[id])
        
        usernames = get_usernames(results)

        #final_result = process_date(final_result)

        return final_result, usernames

    def process(self):
        # files path
        # paths
        path = "./data/"
        # load corpus 
        self.corpus = load_corpus(path+"original_tweets.json")
        self.processed_corpus = load_processed_corpus(path+"processed_tweets.json")
        self.index = create_index(self.processed_corpus)
        num_documents = len(self.processed_corpus.keys())
        self.tf,self.df,self.idf = create_tfidf(self.processed_corpus,num_documents)
        self.newest_date = get_newest_date(self.corpus)


