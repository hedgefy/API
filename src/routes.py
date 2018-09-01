from termcolor import cprint
import hashlib, json, requests, fbprophet
from flask import Flask, jsonify, request
from flask_cors import CORS
try:
    from urllib.parse import urlparse
except ImportError:
     from urlparse import urlparse

app = Flask(__name__)
CORS(app)

@app.route('/coisa', methods=['POST'])
def coisa():
    values = request.get_json()
    ds = values.get('ds')
    y = values.get('y')
    print('values', values.keys())
    if ds is None:
        return "Error: routes.py:17, ds is None"
    print('\n')
    print('api',str(y[:10]))
    print('\n')
    return jsonify({'ds': ds[:10], 'y': y[:10]}), 200



@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()
    nodes = values.get('nodes')
    
    if nodes is None:
        return "Error: line 240, please suppply a valid list of nodes", 400

    for node in nodes:
        blockchain.register_node(node)

    response = {
        'message': 'Nodes {} have been added'.format(nodes),
        'total_nodes': list(blockchain.nodes)
    }
    return jsonify(response), 201
