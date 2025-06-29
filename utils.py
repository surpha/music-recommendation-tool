import re
from typing import Dict, List, Optional, Tuple
import json

def format_duration(ms: int) -> str:
    """
    Convert milliseconds to MM:SS format.
    
    Args:
        ms: Duration in milliseconds
        
    Returns:
        Formatted duration string
    """
    seconds = ms // 1000
    minutes = seconds // 60
    seconds = seconds % 60
    return f"{minutes}:{seconds:02d}"

def format_tempo(bpm: float) -> str:
    """
    Format tempo with appropriate label.
    
    Args:
        bpm: Tempo in BPM
        
    Returns:
        Formatted tempo string
    """
    if bpm < 60:
        return f"{bpm:.0f} BPM (Larghissimo)"
    elif bpm < 66:
        return f"{bpm:.0f} BPM (Largo)"
    elif bpm < 76:
        return f"{bpm:.0f} BPM (Adagio)"
    elif bpm < 108:
        return f"{bpm:.0f} BPM (Andante)"
    elif bpm < 132:
        return f"{bpm:.0f} BPM (Allegro)"
    elif bpm < 168:
        return f"{bpm:.0f} BPM (Vivace)"
    else:
        return f"{bpm:.0f} BPM (Presto)"

def get_key_name(key: int) -> str:
    """
    Convert key number to musical key name.
    
    Args:
        key: Key number (0-11)
        
    Returns:
        Key name string
    """
    keys = ['C', 'C♯/D♭', 'D', 'D♯/E♭', 'E', 'F', 'F♯/G♭', 'G', 'G♯/A♭', 'A', 'A♯/B♭', 'B']
    return keys[key] if 0 <= key <= 11 else 'Unknown'

def get_mode_name(mode: int) -> str:
    """
    Convert mode number to mode name.
    
    Args:
        mode: Mode number (0 or 1)
        
    Returns:
        Mode name string
    """
    return "Minor" if mode == 0 else "Major"

def get_time_signature_name(time_signature: int) -> str:
    """
    Convert time signature number to readable format.
    
    Args:
        time_signature: Time signature number
        
    Returns:
        Time signature string
    """
    return f"{time_signature}/4"

def get_feature_description(feature: str, value: float) -> str:
    """
    Get human-readable description of audio feature value.
    
    Args:
        feature: Feature name
        value: Feature value
        
    Returns:
        Description string
    """
    descriptions = {
        'danceability': {
            'low': 'Not very danceable',
            'medium': 'Moderately danceable',
            'high': 'Very danceable'
        },
        'energy': {
            'low': 'Low energy, calm',
            'medium': 'Moderate energy',
            'high': 'High energy, intense'
        },
        'valence': {
            'low': 'Sad, negative mood',
            'medium': 'Neutral mood',
            'high': 'Happy, positive mood'
        },
        'acousticness': {
            'low': 'Electronic/instrumental',
            'medium': 'Mixed acoustic/electronic',
            'high': 'Acoustic, natural'
        },
        'instrumentalness': {
            'low': 'Contains vocals',
            'medium': 'Mixed vocals/instrumental',
            'high': 'Instrumental only'
        },
        'liveness': {
            'low': 'Studio recording',
            'medium': 'Mixed live/studio',
            'high': 'Live performance'
        },
        'speechiness': {
            'low': 'Musical content',
            'medium': 'Mixed speech/music',
            'high': 'Spoken word content'
        }
    }
    
    if feature not in descriptions:
        return f"{value:.2f}"
    
    if value < 0.33:
        level = 'low'
    elif value < 0.67:
        level = 'medium'
    else:
        level = 'high'
    
    return descriptions[feature][level]

def get_loudness_description(loudness: float) -> str:
    """
    Get description for loudness value.
    
    Args:
        loudness: Loudness in dB
        
    Returns:
        Loudness description
    """
    if loudness < -20:
        return "Very quiet"
    elif loudness < -10:
        return "Quiet"
    elif loudness < 0:
        return "Moderate"
    elif loudness < 5:
        return "Loud"
    else:
        return "Very loud"

def extract_spotify_url_info(url: str) -> Optional[Dict]:
    """
    Extract information from Spotify URL.
    
    Args:
        url: Spotify URL
        
    Returns:
        Dictionary with extracted info or None
    """
    patterns = {
        'track': r'spotify\.com/track/([a-zA-Z0-9]+)',
        'album': r'spotify\.com/album/([a-zA-Z0-9]+)',
        'artist': r'spotify\.com/artist/([a-zA-Z0-9]+)',
        'playlist': r'spotify\.com/playlist/([a-zA-Z0-9]+)'
    }
    
    for url_type, pattern in patterns.items():
        match = re.search(pattern, url)
        if match:
            return {
                'type': url_type,
                'id': match.group(1)
            }
    
    return None

def sanitize_search_query(query: str) -> str:
    """
    Clean and sanitize search query.
    
    Args:
        query: Raw search query
        
    Returns:
        Sanitized query
    """
    # Remove special characters that might cause issues
    query = re.sub(r'[^\w\s\-\.]', '', query)
    # Remove extra whitespace
    query = re.sub(r'\s+', ' ', query).strip()
    return query

def calculate_popularity_score(track: Dict) -> float:
    """
    Calculate a popularity score based on track features.
    
    Args:
        track: Track dictionary
        
    Returns:
        Popularity score (0-1)
    """
    popularity = track.get('popularity', 0) / 100.0
    
    # Bonus for high energy and danceability (generally more popular)
    energy_bonus = track.get('energy', 0.5) * 0.1
    danceability_bonus = track.get('danceability', 0.5) * 0.1
    
    score = popularity + energy_bonus + danceability_bonus
    return min(score, 1.0)

def get_genre_similarity(genres1: List[str], genres2: List[str]) -> float:
    """
    Calculate similarity between two genre lists.
    
    Args:
        genres1: First genre list
        genres2: Second genre list
        
    Returns:
        Similarity score (0-1)
    """
    if not genres1 or not genres2:
        return 0.0
    
    # Convert to sets for easier comparison
    set1 = set(genres1)
    set2 = set(genres2)
    
    # Calculate Jaccard similarity
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    
    return intersection / union if union > 0 else 0.0

def create_feature_vector(track: Dict) -> List[float]:
    """
    Create a feature vector from track data.
    
    Args:
        track: Track dictionary
        
    Returns:
        List of feature values
    """
    features = [
        track.get('danceability', 0),
        track.get('energy', 0),
        track.get('valence', 0),
        track.get('tempo', 120) / 200,  # Normalize tempo
        (track.get('loudness', -60) + 60) / 60,  # Normalize loudness
        track.get('acousticness', 0),
        track.get('instrumentalness', 0),
        track.get('liveness', 0),
        track.get('speechiness', 0)
    ]
    
    return features

def format_similarity_score(score: float) -> str:
    """
    Format similarity score for display.
    
    Args:
        score: Similarity score (0-1)
        
    Returns:
        Formatted score string
    """
    percentage = score * 100
    if percentage >= 90:
        return f"{percentage:.0f}% (Excellent match)"
    elif percentage >= 80:
        return f"{percentage:.0f}% (Very good match)"
    elif percentage >= 70:
        return f"{percentage:.0f}% (Good match)"
    elif percentage >= 60:
        return f"{percentage:.0f}% (Moderate match)"
    else:
        return f"{percentage:.0f}% (Weak match)"

def validate_track_data(track: Dict) -> bool:
    """
    Validate that track data contains required fields.
    
    Args:
        track: Track dictionary
        
    Returns:
        True if valid, False otherwise
    """
    required_fields = ['id', 'name', 'artist']
    audio_features = ['danceability', 'energy', 'valence']
    
    # Check required fields
    for field in required_fields:
        if field not in track or not track[field]:
            return False
    
    # Check if audio features are present
    has_features = any(feature in track for feature in audio_features)
    
    return has_features

def merge_track_data(track_info: Dict, audio_features: Dict) -> Dict:
    """
    Merge track info and audio features into single dictionary.
    
    Args:
        track_info: Basic track information
        audio_features: Audio feature data
        
    Returns:
        Merged track dictionary
    """
    merged = track_info.copy()
    if audio_features:
        merged.update(audio_features)
    return merged

def get_recommendation_reasoning(target_track: Dict, recommended_track: Dict) -> List[str]:
    """
    Generate reasoning for why a track was recommended.
    
    Args:
        target_track: Original track
        recommended_track: Recommended track
        
    Returns:
        List of reasoning strings
    """
    reasons = []
    
    # Compare key features
    features_to_compare = [
        ('danceability', 'danceability'),
        ('energy', 'energy'),
        ('valence', 'valence'),
        ('acousticness', 'acousticness')
    ]
    
    for feature, _ in features_to_compare:
        target_val = target_track.get(feature, 0)
        rec_val = recommended_track.get(feature, 0)
        
        if abs(target_val - rec_val) < 0.1:  # Similar values
            feature_name = feature.replace('_', ' ').title()
            reasons.append(f"Similar {feature_name}")
    
    # Check tempo similarity
    target_tempo = target_track.get('tempo', 120)
    rec_tempo = recommended_track.get('tempo', 120)
    tempo_diff = abs(target_tempo - rec_tempo)
    
    if tempo_diff < 10:
        reasons.append("Similar tempo")
    elif tempo_diff < 30:
        reasons.append("Moderately similar tempo")
    
    # Check key and mode
    if (target_track.get('key') == recommended_track.get('key') and 
        target_track.get('mode') == recommended_track.get('mode')):
        reasons.append("Same musical key and mode")
    
    return reasons[:3]  # Limit to top 3 reasons 