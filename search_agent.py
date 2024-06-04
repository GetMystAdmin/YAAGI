import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

def search_prompts(query):
    # Load the dataset
    df = pd.read_csv('collection/prompt_db/all_prompts.csv')

    # Combine the prompt_template and action columns
    df['content'] = df['prompt_template'] + ' ' + df['action']
    #print(df)

    # Initialize the vectorizer
    tf = TfidfVectorizer(analyzer='word', ngram_range=(1, 3), min_df=0.0, stop_words='english')
    # Fit and transform the vectorizer on content
    tfidf_matrix = tf.fit_transform(df['content'])

    # Compute cosine similarity
    cosine_similarities = linear_kernel(tfidf_matrix, tfidf_matrix)

    # Transform the query
    query_vector = tf.transform([query])

    # Compute cosine similarities for the query
    query_similarities = linear_kernel(query_vector, tfidf_matrix).flatten()

    # Get the best match
    best_match_idx = query_similarities.argmax()
    #best_match_idx = cosine_similarities.argmax()

    # Check if the best match is good enough
    if query_similarities[best_match_idx] > 0:
        # Return the 'agent_name' corresponding to the best match
        return df.loc[best_match_idx, 'filename']
    else:
        # No good match found
        return ''


if __name__ == "__main__":
    agent1 = search_prompts("novel writing bot")
    print(agent1)