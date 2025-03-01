import db
import json
import bson
import pandas as pd
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk

SENTIMENT_THRESHOLD = -0.75

# Download the VADER lexicon
nltk.download('vader_lexicon')

def load_bson_data(file_path, limit=10):
    data = []
    with open(file_path, 'rb') as file:
        for i, item in enumerate(bson.decode_file_iter(file)):
            if i >= limit:
                break
            data.append(item)
    return data

def extract_features(data):
    features = pd.DataFrame()
    features['event_id'] = [item['id'] for item in data]
    features['repo_name'] = [item['repo']['name'] for item in data]
    features['actor_login'] = [item['actor']['login'] for item in data]
    features['actor_display_login'] = [item['actor'].get('display_login', '') for item in data]
    features['commit_messages'] = [
        ' '.join([commit['message'] for commit in item['payload'].get('commits', [])]) for item in data
    ]
    features['description'] = [item['payload'].get('description', '') for item in data]
    features['issue_body'] = [item['payload'].get('issue', {}).get('body', '') for item in data]
    features['reactions_minus_one'] = [item['payload'].get('issue', {}).get('reactions', {}).get('-1', 0) for item in data]
    return features

def filter_by_reactions(data, threshold=5):
    # Extract features
    features = extract_features(data)

    # Filter by the threshold
    filtered_data = features[features['reactions_minus_one'] > threshold]

    return filtered_data

def classify_sentiment(text):
    sid = SentimentIntensityAnalyzer()
    sentiment_scores = sid.polarity_scores(text)
    return sentiment_scores['compound']

def filter_negative_sentiment(data):
    features = extract_features(data)
    features['combined_text'] = features.apply(
        lambda row: ' '.join([
            str(row['repo_name']) if row['repo_name'] else '',
            str(row['actor_login']) if row['actor_login'] else '',
            str(row['actor_display_login']) if row['actor_display_login'] else '',
            str(row['commit_messages']) if row['commit_messages'] else '',
            str(row['description']) if row['description'] else '',
            str(row['issue_body']) if row['issue_body'] else ''
        ]), axis=1
    )
    features['sentiment'] = features['combined_text'].apply(classify_sentiment)
    filtered_data = features[features['sentiment'] >= SENTIMENT_THRESHOLD]  # Filter out negative sentiment
    non_filtered_data = features[features['sentiment'] < SENTIMENT_THRESHOLD]  # Rows that do not pass the filter
    return filtered_data, non_filtered_data

def print_events():
    mongodb = db.get_db_connection()
    events_collections = mongodb['events']

    # Find all documents where type is "IssuesEvent"
    issues_events = events_collections.find({"type": "PushEvent"}).limit(10)

    # Pretty print the resulting documents
    for event in issues_events:
        print(json.dumps(event, indent=4, default=str))

if __name__ == "__main__":
    file_path = './dump/gitfeed/events.bson'
    data = load_bson_data(file_path, 10000)

    filtered_data = filter_by_reactions(data)
    print("Filtered by reactions:")
    print(filtered_data)

    filtered_sentiment_data, non_filtered_sentiment_data = filter_negative_sentiment(data)
    print("Filtered by sentiment:")
    print(filtered_sentiment_data)
    print("Not filtered by sentiment:")
    print(non_filtered_sentiment_data)