from flask import Flask, render_template, request, jsonify
from spotify_client import SpotifyClient
from recommendation_engine import RecommendationEngine
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')

# Initialize Spotify client and recommendation engine
spotify_client = SpotifyClient()
recommendation_engine = RecommendationEngine()

@app.route('/')
def index():
    """Main page route."""
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search_songs():
    """Search for songs using Spotify API."""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({'error': 'Please enter a song name'}), 400
        
        logger.info(f"Searching for: {query}")
        
        # Search for songs
        search_results = spotify_client.search_track(query, limit=50)  # Get more results for filtering
        
        if not search_results:
            return jsonify({'error': 'No songs found. Please try a different search term.'}), 404
        
        # Filter out tracks whose name contains the search query (case-insensitive, normalized)
        def normalize(text):
            return ''.join(text.lower().strip().split())

        query_norm = normalize(query)
        filtered_results = [
            track for track in search_results
            if query_norm not in normalize(track['name'])
        ]

        # Take the first 20 filtered results
        filtered_results = filtered_results[:20]

        if not filtered_results:
            return jsonify({'error': 'No songs found after filtering. Please try a different search term.'}), 404

        # Format results for frontend
        formatted_results = []
        for track in filtered_results:
            formatted_results.append({
                'id': track['id'],
                'name': track['name'],
                'artist': track['artists'][0]['name'] if track['artists'] else 'Unknown Artist',
                'album': track['album']['name'] if track['album'] else 'Unknown Album',
                'image_url': track['album']['images'][0]['url'] if track['album']['images'] else None,
                'preview_url': track.get('preview_url'),
                'external_url': track['external_urls']['spotify'] if 'external_urls' in track else None
            })

        logger.info(f"Found {len(formatted_results)} songs after filtering")
        return jsonify({'songs': formatted_results})
        
    except Exception as e:
        logger.error(f"Error in search: {str(e)}")
        return jsonify({'error': 'An error occurred while searching. Please try again.'}), 500

@app.route('/recommend', methods=['POST'])
def get_recommendations():
    """Get song recommendations based on selected track."""
    try:
        data = request.get_json()
        track_id = data.get('track_id')
        method = data.get('method', 'feature_based')  # Default to feature-based method
        input_track_name = data.get('input_track_name', '').strip().lower()  # New: original search query
        
        if not track_id:
            return jsonify({'error': 'Track ID is required'}), 400
        
        logger.info(f"Getting recommendations for track ID: {track_id} using method: {method}")
        
        # Get track details and audio features
        track_details = spotify_client.get_track(track_id)
        if not track_details:
            return jsonify({'error': 'Track not found'}), 404
        
        audio_features = spotify_client.get_audio_features(track_id)
        if not audio_features:
            return jsonify({'error': 'Audio features not available for this track'}), 404
        
        # Combine track details with audio features
        target_track = {**track_details, **audio_features}
        
        # Get recommendations from Spotify
        spotify_recommendations = spotify_client.get_recommendations(
            seed_tracks=[track_id],
            limit=50  # Get more candidates for better filtering
        )
        
        if not spotify_recommendations:
            return jsonify({'error': 'No recommendations available'}), 404
        
        # Get audio features for all recommended tracks
        recommended_tracks_with_features = []
        for track in spotify_recommendations:
            features = spotify_client.get_audio_features(track['id'])
            if features:
                track_with_features = {**track, **features}
                recommended_tracks_with_features.append(track_with_features)
        
        if not recommended_tracks_with_features:
            return jsonify({'error': 'No tracks with audio features available'}), 404
        
        logger.info(f"Found {len(recommended_tracks_with_features)} tracks with audio features")
        
        # Filter out recommendations whose name contains the input track name (case-insensitive)
        if input_track_name:
            filtered_tracks = [
                t for t in recommended_tracks_with_features
                if input_track_name not in t['name'].lower()
            ]
        else:
            filtered_tracks = recommended_tracks_with_features
        
        # Use recommendation engine to find similar tracks
        if method == 'cosine':
            similar_tracks = recommendation_engine.find_similar_tracks(
                target_track, 
                filtered_tracks,
                n_recommendations=20,
                similarity_method='cosine'
            )
        elif method == 'euclidean':
            similar_tracks = recommendation_engine.find_similar_tracks(
                target_track, 
                filtered_tracks,
                n_recommendations=20,
                similarity_method='euclidean'
            )
        elif method == 'weighted':
            similar_tracks = recommendation_engine.weighted_similarity(
                target_track, 
                filtered_tracks,
                n_recommendations=20
            )
        else:  # feature_based (default)
            similar_tracks = recommendation_engine.feature_based_filtering(
                target_track, 
                filtered_tracks,
                n_recommendations=20
            )
        
        if not similar_tracks:
            return jsonify({'error': 'No similar tracks found'}), 404
        
        # Format results for frontend
        formatted_recommendations = []
        for track, similarity_score in similar_tracks:
            formatted_recommendations.append({
                'id': track['id'],
                'name': track['name'],
                'artist': track['artists'][0]['name'] if track['artists'] else 'Unknown Artist',
                'album': track['album']['name'] if track['album'] else 'Unknown Album',
                'image_url': track['album']['images'][0]['url'] if track['album']['images'] else None,
                'preview_url': track.get('preview_url'),
                'external_url': track['external_urls']['spotify'] if 'external_urls' in track else None,
                'similarity_score': round(similarity_score * 100, 1),  # Show as percentage
                'audio_features': {
                    'danceability': track.get('danceability', 0),
                    'energy': track.get('energy', 0),
                    'valence': track.get('valence', 0),
                    'tempo': track.get('tempo', 0),
                    'acousticness': track.get('acousticness', 0),
                    'instrumentalness': track.get('instrumentalness', 0),
                    'liveness': track.get('liveness', 0),
                    'speechiness': track.get('speechiness', 0)
                }
            })
        
        # Get target track info for display
        target_info = {
            'id': target_track['id'],
            'name': target_track['name'],
            'artist': target_track['artists'][0]['name'] if target_track['artists'] else 'Unknown Artist',
            'album': target_track['album']['name'] if target_track['album'] else 'Unknown Album',
            'image_url': target_track['album']['images'][0]['url'] if target_track['album']['images'] else None,
            'audio_features': {
                'danceability': target_track.get('danceability', 0),
                'energy': target_track.get('energy', 0),
                'valence': target_track.get('valence', 0),
                'tempo': target_track.get('tempo', 0),
                'acousticness': target_track.get('acousticness', 0),
                'instrumentalness': target_track.get('instrumentalness', 0),
                'liveness': target_track.get('liveness', 0),
                'speechiness': target_track.get('speechiness', 0)
            }
        }
        
        logger.info(f"Returning {len(formatted_recommendations)} recommendations")
        
        return jsonify({
            'target_track': target_info,
            'recommendations': formatted_recommendations,
            'method_used': method,
            'total_candidates': len(filtered_tracks)
        })
        
    except Exception as e:
        logger.error(f"Error in recommendations: {str(e)}")
        return jsonify({'error': 'An error occurred while getting recommendations. Please try again.'}), 500

@app.route('/track/<track_id>')
def get_track_details(track_id):
    """Get detailed information about a specific track."""
    try:
        track_details = spotify_client.get_track(track_id)
        if not track_details:
            return jsonify({'error': 'Track not found'}), 404
        
        audio_features = spotify_client.get_audio_features(track_id)
        if audio_features:
            track_details['audio_features'] = audio_features
        
        return jsonify(track_details)
        
    except Exception as e:
        logger.error(f"Error getting track details: {str(e)}")
        return jsonify({'error': 'An error occurred while getting track details.'}), 500

@app.route('/health')
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'message': 'Music Recommendation API is running'})

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    debug = os.getenv('FLASK_ENV') == 'development'
    
    logger.info(f"Starting Music Recommendation API on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug) 