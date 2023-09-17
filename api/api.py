#!/usr/bin/env python
# encoding: utf-8
import json
from flask import Flask, jsonify, request
from main import main
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins='http://localhost:3000') 

@app.route('/', methods=['POST'])
def index():
    data = request.get_json()
    print(data)
    headers = {
        'Access-Control-Allow-Origin': 'http://localhost:3000'
    }
    data = main(data["text"])
    return (data, 200, headers)

app.run(debug=True)
