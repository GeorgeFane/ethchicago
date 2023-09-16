#!/usr/bin/env python
# encoding: utf-8
import json
from flask import Flask, jsonify
from main import main

app = Flask(__name__)

@app.route('/')
def index():
    headers = {
        'Access-Control-Allow-Origin': 'https://jubilant-zebra-547x5w6pj7735j-3000.app.github.dev/'
    }
    data = main()
    return (data, 200, headers)

app.run(debug=True)
