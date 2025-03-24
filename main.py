from flask import Flask, request, jsonify
from apiv2 import process_search_query
from utils import load_nltk

app = Flask(__name__)

@app.route('/search', methods=['POST'])
def search():
    data = request.json
    search_query = data.get('search_query')
    if not search_query:
        return jsonify({"error": "No search query provided"}), 400

    load_nltk()
    result = process_search_query(search_query)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
