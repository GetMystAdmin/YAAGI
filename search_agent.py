import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
import importlib.util

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
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
@cross_origin()
def search():
    data = request.get_json()
    result = search_prompts(data['query'])
    return jsonify({
        'filename': result
    })

@app.route('/ask-ai', methods=['POST'])
@cross_origin()
def ask_ai():
    data = request.get_json()
    filename = data['filename']
    query = data['query']
    # Call the Python script with the filename paramete

    # formulate the full path to the script
    module_path = 'collection/' + filename

    # load and import the module dynamically
    spec = importlib.util.spec_from_file_location(filename, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # call the 'run' function from the module
    generator_object = module.main(query)

    # convert set to list
    list_outputs = [output for output in list(generator_object)]
    # Extract the content from the message object
    content_output = [output[1] for output in list_outputs if output[0] == 'content']
    return jsonify({
        'file_output': content_output
    })


if __name__ == "__main__":
    app.run(debug=True)
