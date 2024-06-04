import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from flask import Flask, request, jsonify

app = Flask(__name__)
def search_prompts(query):
    # Load the dataset
    df = pd.read_csv('collection/prompt_db/all_prompts.csv')

    # Combine the prompt_template and action columns
    df['content'] = df['prompt_template'] + ' ' + df['action']
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
    # Check if the best match is good enough
    if query_similarities[best_match_idx] > 0:
        # Return the 'filename' corresponding to the best match
        return df.loc[best_match_idx, 'filename']
    else:
        # No good match found
        return ''


@app.route('/search', methods=['POST'])
def search():
    data = request.get_json()
    result = search_prompts(data['query'])
    return jsonify({
        'filename': result
    })


if __name__ == "__main__":
    app.run(debug=True)
