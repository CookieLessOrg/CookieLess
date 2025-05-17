from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime, timedelta

app = Flask(__name__)

# MongoDB setup
client = MongoClient("mongodb://mongodb:27017/")
db = client["cookieless"]
data_collection = db["visits"]

def get_time_periods():
    now = datetime.now()
    return {
        "day": now - timedelta(days=1),
        "month": now - timedelta(days=30),
        "all_time": datetime.min
    }

@app.route('/post', methods=['POST'])
def log_data():
    data = request.get_json()
    data["timestamp"] = datetime.now()
    data_collection.insert_one(data)
    return jsonify({"status": "success"}), 200

@app.route('/get', methods=['GET'])
def get_stats():
    
    # Daily statistics
    daily_stats = list(data_collection.aggregate([
        {
            "$group": {
                "_id": {
                    "$dateToString": {
                        "format": "%Y-%m-%d", 
                        "date": "$timestamp"
                    }
                },
                "total": {"$sum": 1},
                "unique": {"$addToSet": "$fingerprint"}
            }
        },
        {
            "$project": {
                "date": "$_id",
                "total": 1,
                "unique": {"$size": "$unique"},
                "_id": 0
            }
        },
        {"$sort": {"date": 1}}
    ]))
    
    # Monthly statistics
    monthly_stats = list(data_collection.aggregate([
        {
            "$group": {
                "_id": {
                    "$dateToString": {
                        "format": "%Y-%m", 
                        "date": "$timestamp"
                    }
                },
                "total": {"$sum": 1},
                "unique": {"$addToSet": "$fingerprint"}
            }
        },
        {
            "$project": {
                "month": "$_id",
                "total": 1,
                "unique": {"$size": "$unique"},
                "_id": 0
            }
        },
        {"$sort": {"month": 1}}
    ]))
    
    # Time period statistics (last 24h, last 30d, all-time)
    periods = get_time_periods()
    period_stats = {}
    
    for period, start_date in periods.items():
        period_stats[period] = {
            "total": data_collection.count_documents({"timestamp": {"$gte": start_date}}),
            "unique": len(data_collection.distinct("fingerprint", {"timestamp": {"$gte": start_date}}))
        }
    
    return jsonify({
        "dailyStats": daily_stats,
        "monthlyStats": monthly_stats,
        "periodStats": period_stats
    }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)