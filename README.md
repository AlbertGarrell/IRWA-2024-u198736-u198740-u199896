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
- Removed emojis

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

---

# IRWA Project 2024 - Part 2

In Part 2, we extended our search engine's functionality by developing core indexing and evaluation methods. This phase included building an inverted index for tweet content and implementing a hybrid ranking approach that combines TF-IDF scores with BERT-based similarity scores for hashtags. Our method prioritizes tweets based on both content and hashtag relevance, with evaluation metrics to assess the search engine's retrieval performance.

### Instructions to run the code:

1. Download the following files from the Part 2 folder in the GitHub repository:
   - `original_tweets.json` (raw, unprocessed tweets)
   - `processed_tweets.json` (tokenized and processed tweet content for indexing)
   - `evaluation_gt` (ground truth file for evaluation)
2. Place these files in your working directory.
3. Open the notebook `IRWA_2024_part_2.ipynb` in your preferred environment (Google Colab, Jupyter, etc.).
4. Adjust file paths in the notebook to the appropriate file locations.
5. Run each cell to build the inverted index, process queries, and evaluate search engine performance.
6. The notebook includes installation steps for necessary libraries such as BERT and evaluation metrics.

### Requirements

- Python 3.x
- Libraries: `pandas`, `nltk`, `torch`, `transformers` (for BERT), `sklearn`
- Files: `original_tweets.json`, `processed_tweets.json`, `evaluation_gt`

Make sure the files are correctly loaded, and all necessary dependencies are installed before running the notebook.

---

# IRWA Project 2024 - Part 3

In Part 3, we implement and evaluate four ranking methods to retrieve relevant tweets for given queries, 
considering both term-based and contextual relevance. The four methods tested are:

1. **TF-IDF + Cosine Similarity + BERT**: Combines TF-IDF term relevance with BERT-based hashtag similarity to capture semantic relevance.
2. **Our Score + Cosine Similarity**: A custom ranking approach that integrates TF-IDF with popularity metrics (likes, retweets, comments, and recency).
3. **BM25**: A probabilistic ranking model balancing term frequency saturation and document length.
4. **Word2Vec + Cosine Similarity**: Uses word embeddings to capture contextual relevance in tweets.

Our GitHub repository contains code and documentation for this part, tagged as `IRWA-2024-part-3`.

### Instructions to run the code:

1. Place the following files in your working directory:
   - `original_tweets.json` (raw tweet data)
   - `processed_tweets.json` (tokenized and processed tweet data)
2. Open the notebook `IRWA_2024_part_3.ipynb` in your preferred environment (Google Colab, Jupyter, etc.).
3. Update file paths in the notebook as needed to match the location of your files.
4. Run each cell to:
   - Load and preprocess the dataset.
   - Build the inverted index.
   - Execute each ranking method on specified queries.
5. The code includes steps to install necessary libraries such as `gensim` (for Word2Vec) and `sentence_transformers` (for BERT embeddings).

### Requirements

- Python 3.x
- Libraries: `pandas`, `nltk`, `torch`, `transformers` (for BERT), `gensim` (for Word2Vec), `scipy`
- Files: `original_tweets.json`, `processed_tweets.json`

Ensure all required files are loaded, and necessary dependencies are installed before running the notebook.
