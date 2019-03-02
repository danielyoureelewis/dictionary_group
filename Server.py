#!/usr/bin/python3
# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify
import json
from wsd import wsddef
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False 

@app.route('/get_def', methods=['POST'])
def get_definition():
    definition = wsddef.get_def(request.json) 
    return jsonify(definition)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4321, debug=True)
