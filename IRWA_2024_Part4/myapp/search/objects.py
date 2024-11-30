import json


class Document:
    """
    Original corpus data as an object
    """

    def __init__(self, id, title, description, doc_date, likes, retweets, url, hashtags,comments):
        self.id = id
        self.title = title
        self.tweet = description
        self.date = doc_date
        self.likes = likes
        self.retweets = retweets
        self.url = url
        self.hashtags = hashtags
        self.comment_count = comments

    def get_date(self):
        return self.date

    def get_id(self):
        return self.id

    def get_title(self):
        return self.title

    def get_tweet(self):
        return self.tweet
    
    def get_likes(self):
        return self.likes
    
    def get_retweets(self):
        return self.retweets

    def get_url(self):
        return self.url

    def get_hashtags(self):
        return self.hashtags

    def get_comment_count(self):
        return self.comment_count

    

    def to_json(self):
        return self.__dict__

    def __str__(self):
        """
        Print the object content as a JSON string
        """
        return json.dumps(self)


class StatsDocument:
    """
    Original corpus data as an object
    """

    def __init__(self, id, title, description, doc_date, url, count):
        self.id = id
        self.title = title
        self.description = description
        self.doc_date = doc_date
        self.url = url
        self.count = count

    def __str__(self):
        """
        Print the object content as a JSON string
        """
        return json.dumps(self)


class ResultItem:
    def __init__(self, id, title, description, doc_date, url, ranking):
        self.id = id
        self.title = title
        self.description = description
        self.doc_date = doc_date
        self.url = url
        self.ranking = ranking
