#!/usr/bin/env python
# encoding: utf-8
import json
from flask import Flask, jsonify
from main import main

app = Flask(__name__)

@app.route('/')
def index():
    headers = {
        'Access-Control-Allow-Origin': 'http://localhost:3000'
    }
    data = main()
    return (data, 200, headers)

app.run(debug=True)
