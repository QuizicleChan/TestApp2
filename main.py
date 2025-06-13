
from flask import Flask, render_template, request, jsonify
import json
from datetime import datetime, timedelta
import random

app = Flask(__name__)

# Sample ride data for Universal Orlando Florida
RIDES_DATA = {
    "Harry Potter and the Forbidden Journey": {
        "location": "Islands of Adventure - Wizarding World",
        "avg_wait_time": 45,
        "thrill_level": 8,
        "duration": 4,
        "popularity": 9
    },
    "The Incredible Hulk Coaster": {
        "location": "Islands of Adventure - Marvel",
        "avg_wait_time": 35,
        "thrill_level": 9,
        "duration": 2,
        "popularity": 8
    },
    "Jurassic Park River Adventure": {
        "location": "Islands of Adventure - Jurassic Park",
        "avg_wait_time": 25,
        "thrill_level": 6,
        "duration": 6,
        "popularity": 7
    },
    "The Amazing Adventures of Spider-Man": {
        "location": "Islands of Adventure - Marvel",
        "avg_wait_time": 30,
        "thrill_level": 7,
        "duration": 4,
        "popularity": 8
    },
    "Transformers: The Ride 3D": {
        "location": "Universal Studios - Transformers",
        "avg_wait_time": 40,
        "thrill_level": 7,
        "duration": 4,
        "popularity": 8
    },
    "The Mummy": {
        "location": "Universal Studios - New York",
        "avg_wait_time": 30,
        "thrill_level": 8,
        "duration": 3,
        "popularity": 7
    },
    "Despicable Me Minion Mayhem": {
        "location": "Universal Studios - Production Central",
        "avg_wait_time": 20,
        "thrill_level": 4,
        "duration": 5,
        "popularity": 6
    },
    "The Simpsons Ride": {
        "location": "Universal Studios - Springfield",
        "avg_wait_time": 25,
        "thrill_level": 5,
        "duration": 6,
        "popularity": 6
    }
}

def calculate_ride_score(ride_data, preferences):
    """Calculate a score for each ride based on user preferences"""
    thrill_weight = preferences.get('thrill_preference', 5) / 10
    wait_penalty = preferences.get('max_wait_time', 60) / 60
    
    # Higher score is better
    thrill_score = (ride_data['thrill_level'] * thrill_weight) if preferences.get('thrill_preference', 5) > 5 else (10 - ride_data['thrill_level']) * (1 - thrill_weight)
    wait_score = max(0, (preferences.get('max_wait_time', 60) - ride_data['avg_wait_time']) / preferences.get('max_wait_time', 60))
    popularity_score = ride_data['popularity'] / 10
    
    return (thrill_score * 0.4) + (wait_score * 0.4) + (popularity_score * 0.2)

def optimize_route(preferences):
    """Optimize the route based on user preferences"""
    # Filter rides based on preferences
    suitable_rides = {}
    
    for ride_name, ride_data in RIDES_DATA.items():
        if ride_data['avg_wait_time'] <= preferences.get('max_wait_time', 60):
            if preferences.get('min_thrill', 1) <= ride_data['thrill_level'] <= preferences.get('max_thrill', 10):
                suitable_rides[ride_name] = ride_data
    
    # Calculate scores and sort
    ride_scores = []
    for ride_name, ride_data in suitable_rides.items():
        score = calculate_ride_score(ride_data, preferences)
        ride_scores.append((ride_name, ride_data, score))
    
    # Sort by score (highest first)
    ride_scores.sort(key=lambda x: x[2], reverse=True)
    
    # Create optimized itinerary
    itinerary = []
    total_time = 0
    visit_time = datetime.strptime("09:00", "%H:%M")
    
    for ride_name, ride_data, score in ride_scores:
        if total_time + ride_data['avg_wait_time'] + ride_data['duration'] <= preferences.get('available_hours', 8) * 60:
            start_time = visit_time.strftime("%H:%M")
            visit_time += timedelta(minutes=ride_data['avg_wait_time'] + ride_data['duration'])
            end_time = visit_time.strftime("%H:%M")
            
            itinerary.append({
                'ride_name': ride_name,
                'location': ride_data['location'],
                'start_time': start_time,
                'end_time': end_time,
                'wait_time': ride_data['avg_wait_time'],
                'duration': ride_data['duration'],
                'thrill_level': ride_data['thrill_level'],
                'score': round(score, 2)
            })
            
            total_time += ride_data['avg_wait_time'] + ride_data['duration']
            visit_time += timedelta(minutes=10)  # Travel time between rides
    
    return itinerary

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/optimize', methods=['POST'])
def optimize():
    preferences = {
        'max_wait_time': int(request.form.get('max_wait_time', 60)),
        'min_thrill': int(request.form.get('min_thrill', 1)),
        'max_thrill': int(request.form.get('max_thrill', 10)),
        'thrill_preference': int(request.form.get('thrill_preference', 5)),
        'available_hours': int(request.form.get('available_hours', 8))
    }
    
    optimized_route = optimize_route(preferences)
    
    return jsonify({
        'success': True,
        'itinerary': optimized_route,
        'total_rides': len(optimized_route)
    })

@app.route('/rides')
def get_rides():
    return jsonify(RIDES_DATA)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
