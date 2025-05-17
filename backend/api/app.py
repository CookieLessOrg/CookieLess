from flask import Flask, request, jsonify, send_from_directory
from pymongo import MongoClient
from datetime import datetime, timedelta
import threading
import time
import os
import json
from statistics import generate_statistics_images

# Configuration
STATS_DIR = "/var/www/stats"
JSON_FILE = os.path.join(STATS_DIR, "fast_statistics")
IMAGE_PATTERN = os.path.join(STATS_DIR, "stats{}.png")

def get_time_periods():
    now = datetime.now()
    return {
        "day": now - timedelta(days=1),
        "month": now - timedelta(days=30),
        "all_time": datetime.min
    }

def update_stats_file(app):
    """Background task to update statistics JSON file"""
    while True:
        try:
            with app.app_context():
                periods = get_time_periods()
                period_stats = {}
                
                for period, start_date in periods.items():
                    period_stats[period] = {
                        "total": app.data_collection.count_documents({"timestamp": {"$gte": start_date}}),
                        "unique": len(app.data_collection.distinct("fingerprint", {"timestamp": {"$gte": start_date}}))
                    }
                
                stats_data = {"periodStats": period_stats}
                
                with open(JSON_FILE, 'w') as f:
                    json.dump(stats_data, f)
                
                generate_statistics_images(stats_data, IMAGE_PATTERN)
                
        except Exception as e:
            app.logger.error(f"Error updating stats: {str(e)}")
        
        time.sleep(30)

def create_app():
    app = Flask(__name__)
    
    # Initialize MongoDB connection
    mongo_uri = os.getenv("MONGO_URI", "mongodb://mongodb:27017/")
    app.client = MongoClient(mongo_uri)
    app.db = app.client["cookieless"]
    app.data_collection = app.db["visits"]

    # Create stats directory if not exists
    os.makedirs(STATS_DIR, exist_ok=True)

    # Start background thread
    thread = threading.Thread(target=update_stats_file, args=(app,))
    thread.daemon = True
    thread.start()

    return app

app = create_app()

@app.route('/post', methods=['POST'])
def log_data():
    data = request.get_json()
    data["timestamp"] = datetime.now()
    app.data_collection.insert_one(data)
    return jsonify({"status": "success"}), 200

@app.route('/get', methods=['GET'])
def deprecated_get():
    return jsonify({
        "error": "Deprecated method",
        "message": "Please use /fast_statistics instead"
    }), 410

@app.route('/stats<int:num>.png')
def get_stat_image(num):
    try:
        return send_from_directory(STATS_DIR, f"stats{num}.png", mimetype='image/png')
    except FileNotFoundError:
        return jsonify({"error": "Image not found"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)