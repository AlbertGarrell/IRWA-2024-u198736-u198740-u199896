# IRWA-2024-u198736-u198740-u199896
Authors:
- Jaume Camps Romaguera
- Arol Garcia Rodríguez
- Albert Garrell Golobardes

# IRWA Project 2024 - Part 1

In the first part of our project, we focused on understanding and processing the dataset of tweets related to the 2021 Farmers Protests (`farmers_protest_tweets.json`). This involved pre-processing the data, including extracting key information such as the tweet text, date, hashtags, likes, retweets, and URLs. Additionally, we applied several text cleaning techniques to the tweet content and hashtags.
### Tweet Content Handling
- Removed URLs
- Converted text to lowercase
- Removed punctuation and special characters
- Tokenized the words
- Removed stop words
- Applied stemming to reduce words to their root form
- Removed the emojis

Hashtags and usernames were handled with care:
- The `#` symbol was removed, but the words starting with it were retained.
- The `@` symbol was removed, but the usernames were kept for potential future analysis.

### Hashtag Handling:
- Hashtags were extracted from the tweet text while keeping the # symbol during extraction.
- Punctuation (except numbers) was removed from the hashtags.
- Stop words were removed, and the remaining words were stemmed. Hashtags were processed separately from the tweet text to maintain their importance.
- After extraction, hashtags were excluded from the tweet content to ensure they were handled independently.
### Date Conversion:
We also converted the tweet dates to pandas `datetime` objects to enable time-based analysis. 
### Dictionaries Generated:
Two dictionaries were generated for this project:
- `original_tweets_dict`: Contains unprocessed tweet data (tweet text, date, hashtags, likes, retweets, and URLs).
- `processed_tweets_dict`: Contains tokenized and stemmed versions of the tweets, along with the processed hashtags. These dictionaries are linked to document IDs and will be used for indexing and classification in future project stages.

In addition, the file `tweet_document_ids_map.csv` was used to map the tweet data to document IDs. This file provides a correspondence between the tweet IDs and document IDs, ensuring consistency across future project phases.

## Instructions to run the code:

1. Place the following files in the working directory:
   - `IRWA_2024_part_1.ipynb` (the Python notebook)
   - `farmers_protest_tweets.json` (the dataset)
   - `tweet_document_ids_map.csv` (to map tweet IDs to document IDs)
2. Open the notebook in your preferred environment (Google Colab, Jupyter, etc.).
3. Adjust the file paths in the notebook to match the location of your files.
4. Execute each step of the notebook to perform text processing and exploratory data analysis (EDA).
5. The code includes steps to install necessary libraries such as NLTK and WordCloud.

## Exploratory Data Analysis (EDA)

For EDA, the following analyses were performed:
- A word count distribution histogram.
- The average sentence length calculation.
- Vocabulary size determination.
- Ranking of tweets by retweet count.
- Word cloud visualizations for both frequent words and hashtags.
- Hashtag count distribution analysis.

## Requirements

- Python 3.x
- Libraries: `nltk`, `pandas`, `matplotlib`, `seaborn`, `wordcloud`, `spacy`
- Files: `farmers_protest_tweets.json`, `tweet_document_ids_map.csv`

Ensure that all required files are correctly loaded and that the necessary dependencies are installed before running the notebook.
