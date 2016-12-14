
import json

import search

from flask import Flask
app = Flask(__name__)


@app.route('/')
def hello_world():
    wt = search.word_tokenizer
    return json.dumps({"name": "test"})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
