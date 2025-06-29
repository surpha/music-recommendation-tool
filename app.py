from flask import Flask, render_template, request, jsonify, session
from spotify_client import SpotifyClient
from recommendation_engine import RecommendationEngine
from utils import (
    format_duration, format_tempo, get_key_name, get_mode_name,
    get_feature_description, get_loudness_description, extract_spotify_url_info,
    sanitize_search_query, format_similarity_score, get_recommendation_reasoning
)
import os
from dotenv import load_dotenv
import json

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here')

# Initialize clients
try:
    spotify_client = SpotifyClient()
    recommendation_engine = RecommendationEngine()
    print("✅ Spotify client and recommendation engine initialized successfully!")
except Exception as e:
    print(f"❌ Error initializing clients: {e}")
    spotify_client = None
    recommendation_engine = None

@app.route('/')
def index():
    """Main dashboard page."""
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search_tracks():
    """Search for tracks by query."""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        # Check if it's a Spotify URL
        url_info = extract_spotify_url_info(query)
        if url_info and url_info['type'] == 'track':
            # Get track directly by ID
            track_features = spotify_client.get_track_features(url_info['id'])
            if track_features:
                return jsonify({
                    'tracks': [track_features],
                    'message': 'Track found from URL'
                })
        
        # Search by query
        sanitized_query = sanitize_search_query(query)
        tracks = spotify_client.search_track(sanitized_query, limit=10)
        
        if not tracks:
            return jsonify({'error': 'No tracks found'}), 404
        
        return jsonify({
            'tracks': tracks,
            'message': f'Found {len(tracks)} tracks'
        })
        
    except Exception as e:
        print(f"Error in search: {e}")
        return jsonify({'error': 'Search failed'}), 500

@app.route('/recommendations', methods=['POST'])
def get_recommendations():
    """Get song recommendations based on a track using feature-based filtering."""
    try:
        data = request.get_json()
        track_id = data.get('track_id')
        method = data.get('method', 'feature_based')  # feature_based, cosine, euclidean, weighted
        limit = data.get('limit', 20)
        
        if not track_id:
            return jsonify({'error': 'Track ID is required'}), 400
        
        # Get target track features
        target_track = spotify_client.get_track_features(track_id)
        if not target_track:
            return jsonify({'error': 'Target track not found'}), 404
        
        # Get a larger pool of recommendations from Spotify
        # We'll get more recommendations and then filter by features
        spotify_recommendations = spotify_client.get_recommendations(track_id, limit=50)
        
        if not spotify_recommendations:
            return jsonify({'error': 'No recommendations found'}), 404
        
        # Get audio features for recommended tracks
        rec_track_ids = [track['id'] for track in spotify_recommendations]
        rec_features = spotify_client.get_multiple_track_features(rec_track_ids)
        
        if not rec_features:
            return jsonify({'error': 'Could not get audio features'}), 500
        
        # Filter tracks by feature ranges first (remove tracks that are too different)
        filtered_tracks = recommendation_engine.filter_by_feature_ranges(
            target_track, rec_features, tolerance=0.4
        )
        
        if not filtered_tracks:
            # If no tracks pass the filter, use all tracks
            filtered_tracks = rec_features
        
        # Use our recommendation engine to rank them based on the selected method
        if method == 'feature_based':
            similar_tracks = recommendation_engine.feature_based_filtering(
                target_track, filtered_tracks, n_recommendations=limit
            )
        elif method == 'weighted':
            similar_tracks = recommendation_engine.weighted_similarity(
                target_track, filtered_tracks, n_recommendations=limit
            )
        else:
            similar_tracks = recommendation_engine.find_similar_tracks(
                target_track, filtered_tracks, n_recommendations=limit, 
                similarity_method=method
            )
        
        # Format recommendations with similarity scores and reasoning
        formatted_recommendations = []
        for track, similarity_score in similar_tracks:
            reasoning = get_recommendation_reasoning(target_track, track)
            formatted_track = {
                **track,
                'similarity_score': similarity_score,
                'similarity_percentage': format_similarity_score(similarity_score),
                'reasoning': reasoning
            }
            formatted_recommendations.append(formatted_track)
        
        # Calculate diversity score
        diversity_score = recommendation_engine.get_diversity_score([track for track, _ in similar_tracks])
        
        return jsonify({
            'target_track': target_track,
            'recommendations': formatted_recommendations,
            'diversity_score': diversity_score,
            'method': method,
            'message': f'Found {len(formatted_recommendations)} recommendations based on audio features'
        })
        
    except Exception as e:
        print(f"Error in recommendations: {e}")
        return jsonify({'error': 'Failed to get recommendations'}), 500

@app.route('/track/<track_id>')
def get_track_details(track_id):
    """Get detailed information about a specific track."""
    try:
        track_features = spotify_client.get_track_features(track_id)
        if not track_features:
            return jsonify({'error': 'Track not found'}), 404
        
        # Format track data for display
        formatted_track = {
            'id': track_features['id'],
            'name': track_features['name'],
            'artist': track_features['artist'],
            'album': track_features['album'],
            'popularity': track_features['popularity'],
            'external_url': track_features['external_url'],
            'preview_url': track_features['preview_url'],
            'features': {
                'danceability': {
                    'value': track_features.get('danceability', 0),
                    'description': get_feature_description('danceability', track_features.get('danceability', 0))
                },
                'energy': {
                    'value': track_features.get('energy', 0),
                    'description': get_feature_description('energy', track_features.get('energy', 0))
                },
                'valence': {
                    'value': track_features.get('valence', 0),
                    'description': get_feature_description('valence', track_features.get('valence', 0))
                },
                'tempo': {
                    'value': track_features.get('tempo', 120),
                    'description': format_tempo(track_features.get('tempo', 120))
                },
                'loudness': {
                    'value': track_features.get('loudness', -60),
                    'description': get_loudness_description(track_features.get('loudness', -60))
                },
                'acousticness': {
                    'value': track_features.get('acousticness', 0),
                    'description': get_feature_description('acousticness', track_features.get('acousticness', 0))
                },
                'instrumentalness': {
                    'value': track_features.get('instrumentalness', 0),
                    'description': get_feature_description('instrumentalness', track_features.get('instrumentalness', 0))
                },
                'liveness': {
                    'value': track_features.get('liveness', 0),
                    'description': get_feature_description('liveness', track_features.get('liveness', 0))
                },
                'speechiness': {
                    'value': track_features.get('speechiness', 0),
                    'description': get_feature_description('speechiness', track_features.get('speechiness', 0))
                },
                'key': {
                    'value': track_features.get('key', 0),
                    'description': get_key_name(track_features.get('key', 0))
                },
                'mode': {
                    'value': track_features.get('mode', 1),
                    'description': get_mode_name(track_features.get('mode', 1))
                },
                'time_signature': {
                    'value': track_features.get('time_signature', 4),
                    'description': f"{track_features.get('time_signature', 4)}/4"
                }
            }
        }
        
        return jsonify(formatted_track)
        
    except Exception as e:
        print(f"Error getting track details: {e}")
        return jsonify({'error': 'Failed to get track details'}), 500

@app.route('/analyze', methods=['POST'])
def analyze_tracks():
    """Analyze and compare multiple tracks."""
    try:
        data = request.get_json()
        track_ids = data.get('track_ids', [])
        
        if not track_ids:
            return jsonify({'error': 'Track IDs are required'}), 400
        
        # Get features for all tracks
        track_features = spotify_client.get_multiple_track_features(track_ids)
        
        if not track_features:
            return jsonify({'error': 'Could not get track features'}), 500
        
        # Get feature summary
        feature_summary = recommendation_engine.get_feature_summary(track_features)
        
        # Cluster tracks
        clusters = recommendation_engine.cluster_tracks(track_features, n_clusters=3)
        
        # Calculate diversity
        diversity_score = recommendation_engine.get_diversity_score(track_features)
        
        # Add cluster info to tracks
        for i, track in enumerate(track_features):
            track['cluster'] = clusters[i] if i < len(clusters) else 0
        
        return jsonify({
            'tracks': track_features,
            'feature_summary': feature_summary,
            'clusters': clusters,
            'diversity_score': diversity_score,
            'message': f'Analyzed {len(track_features)} tracks'
        })
        
    except Exception as e:
        print(f"Error in analysis: {e}")
        return jsonify({'error': 'Analysis failed'}), 500

@app.route('/health')
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'spotify_client': spotify_client is not None,
        'recommendation_engine': recommendation_engine is not None
    })

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    print(f"🎵 Music Recommendation Tool starting on port {port}")
    print(f"🌐 Open http://localhost:{port} in your browser")
    
    app.run(host='0.0.0.0', port=port, debug=debug) 