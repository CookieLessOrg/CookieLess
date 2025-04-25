from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)

# MongoDB setup
client = MongoClient("mongodb://mongodb:27017/")
db = client["cookieless"]
data_collection = db["visits"]

@app.route('/log', methods=['POST'])
def log_data():
    data = request.get_json()
    data["timestamp"] = datetime.now()
    data_collection.insert_one(data)
    return jsonify({"status": "success"}), 200

@app.route('/stats', methods=['GET'])
def get_stats():
    total_visitors = data_collection.count_documents({})
    return jsonify({"totalVisitors": total_visitors}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)