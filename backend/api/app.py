from flask import Flask, request, jsonify, send_from_directory
from pymongo import MongoClient
from datetime import datetime, timedelta
import threading
import time
import os
import json
from statistics import generate_statistics_images  # New import

# MongoDB setup
client = MongoClient("mongodb://mongodb:27017/")
db = client["cookieless"]
data_collection = db["visits"]

# Configuration
STATS_DIR = "/var/www/stats"
JSON_FILE = f"{STATS_DIR}/fast_statistics.json"
IMAGE_PATTERN = f"{STATS_DIR}/stats{{}}.png"


def create_app():
    app = Flask(__name__)
    
    # Create stats directory if not exists
    os.makedirs(STATS_DIR, exist_ok=True)
    
    # Start update thread
    thread = threading.Thread(target=update_stats_file)
    thread.daemon = True
    thread.start()
    
    return app

app = create_app()


def get_time_periods():
    now = datetime.now()
    return {
        "day": now - timedelta(days=1),
        "month": now - timedelta(days=30),
        "all_time": datetime.min
    }

def update_stats_file():
    """Background task to update statistics JSON file"""
    with app.app_context():
        while True:
            try:
                periods = get_time_periods()
                period_stats = {}
                
                for period, start_date in periods.items():
                    period_stats[period] = {
                        "total": data_collection.count_documents({"timestamp": {"$gte": start_date}}),
                        "unique": len(data_collection.distinct("fingerprint", {"timestamp": {"$gte": start_date}}))
                    }
                
                stats_data = {"periodStats": period_stats}
                
                with open(JSON_FILE, 'w') as f:
                    json.dump(stats_data, f)
                
                # Generate new images
                generate_statistics_images(stats_data, IMAGE_PATTERN)
                
            except Exception as e:
                app.logger.error(f"Error updating stats: {str(e)}")
            
            time.sleep(30)

@app.route('/post', methods=['POST'])
def log_data():
    data = request.get_json()
    data["timestamp"] = datetime.now()
    data_collection.insert_one(data)
    return jsonify({"status": "success"}), 200

@app.route('/get', methods=['GET'])
def deprecated_get():
    return jsonify({
        "error": "Deprecated method",
        "message": "Please use /fast_statistics.json instead"
    }), 410  # Gone status code

@app.route('/stats<int:num>.png')
def get_stat_image(num):
    try:
        return send_from_directory(STATS_DIR, f"stats{num}.png", mimetype='image/png')
    except FileNotFoundError:
        return jsonify({"error": "Image not found"}), 404

# Start background thread when app starts
@app.before_first_request
def initialize():
    # Create stats directory if not exists
    os.makedirs(STATS_DIR, exist_ok=True)
    
    # Start update thread
    thread = threading.Thread(target=update_stats_file)
    thread.daemon = True
    thread.start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)