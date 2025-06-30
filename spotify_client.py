import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv
import pandas as pd
from typing import List, Dict, Optional, Tuple

load_dotenv()

class SpotifyClient:
    def __init__(self):
        """Initialize Spotify client with credentials."""
        self.client_id = os.getenv('SPOTIFY_CLIENT_ID')
        self.client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
        
        if not self.client_id or not self.client_secret:
            raise ValueError("Spotify credentials not found. Please set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET in .env file")
        
        self.sp = spotipy.Spotify(
            client_credentials_manager=SpotifyClientCredentials(
                client_id=self.client_id,
                client_secret=self.client_secret
            )
        )
    
    def search_track(self, query: str, limit: int = 5) -> List[Dict]:
        """
        Search for tracks by query string.
        
        Args:
            query: Search query (song name, artist, etc.)
            limit: Maximum number of results to return
            
        Returns:
            List of track dictionaries with basic info
        """
        try:
            results = self.sp.search(q=query, type='track', limit=limit)
            tracks = []
            
            for track in results['tracks']['items']:
                track_info = {
                    'id': track['id'],
                    'name': track['name'],
                    'artists': track['artists'],
                    'album': track['album'],
                    'release_date': track['album']['release_date'],
                    'popularity': track['popularity'],
                    'duration_ms': track['duration_ms'],
                    'external_urls': track['external_urls'],
                    'preview_url': track['preview_url']
                }
                tracks.append(track_info)
            
            return tracks
        except Exception as e:
            print(f"Error searching tracks: {e}")
            return []
    
    def get_track(self, track_id: str) -> Optional[Dict]:
        """
        Get track information by ID.
        
        Args:
            track_id: Spotify track ID
            
        Returns:
            Track information dictionary
        """
        try:
            track = self.sp.track(track_id)
            return track
        except Exception as e:
            print(f"Error getting track: {e}")
            return None
    
    def get_audio_features(self, track_id: str) -> Optional[Dict]:
        """
        Get audio features for a specific track.
        
        Args:
            track_id: Spotify track ID
            
        Returns:
            Dictionary containing audio features
        """
        try:
            features = self.sp.audio_features(track_id)[0]
            return features
        except Exception as e:
            print(f"Error getting audio features: {e}")
            return None
    
    def get_track_features(self, track_id: str) -> Optional[Dict]:
        """
        Get audio features for a specific track.
        
        Args:
            track_id: Spotify track ID
            
        Returns:
            Dictionary containing audio features
        """
        try:
            features = self.sp.audio_features(track_id)[0]
            if features:
                # Add track info to features
                track_info = self.sp.track(track_id)
                features.update({
                    'name': track_info['name'],
                    'artist': track_info['artists'][0]['name'],
                    'album': track_info['album']['name'],
                    'popularity': track_info['popularity'],
                    'external_url': track_info['external_urls']['spotify'],
                    'preview_url': track_info['preview_url']
                })
            return features
        except Exception as e:
            print(f"Error getting track features: {e}")
            return None
    
    def get_recommendations(self, seed_tracks: List[str], limit: int = 20) -> List[Dict]:
        """
        Get Spotify's recommended tracks based on seed tracks.
        
        Args:
            seed_tracks: List of seed track IDs
            limit: Number of recommendations to return
            
        Returns:
            List of recommended track dictionaries
        """
        try:
            recommendations = self.sp.recommendations(
                seed_tracks=seed_tracks,
                limit=limit
            )
            
            recommended_tracks = []
            for track in recommendations['tracks']:
                track_info = {
                    'id': track['id'],
                    'name': track['name'],
                    'artists': track['artists'],
                    'album': track['album'],
                    'popularity': track['popularity'],
                    'external_urls': track['external_urls'],
                    'preview_url': track['preview_url']
                }
                recommended_tracks.append(track_info)
            
            return recommended_tracks
        except Exception as e:
            print(f"Error getting recommendations: {e}")
            return []
    
    def get_multiple_track_features(self, track_ids: List[str]) -> List[Dict]:
        """
        Get audio features for multiple tracks efficiently.
        
        Args:
            track_ids: List of Spotify track IDs
            
        Returns:
            List of track feature dictionaries
        """
        try:
            # Get features in batches (Spotify API limit is 100)
            all_features = []
            batch_size = 100
            
            for i in range(0, len(track_ids), batch_size):
                batch = track_ids[i:i + batch_size]
                features_batch = self.sp.audio_features(batch)
                
                # Get track info for the batch
                tracks_batch = self.sp.tracks(batch)['tracks']
                
                for j, features in enumerate(features_batch):
                    if features and tracks_batch[j]:
                        track_info = tracks_batch[j]
                        features.update({
                            'name': track_info['name'],
                            'artist': track_info['artists'][0]['name'],
                            'album': track_info['album']['name'],
                            'popularity': track_info['popularity'],
                            'external_url': track_info['external_urls']['spotify'],
                            'preview_url': track_info['preview_url']
                        })
                        all_features.append(features)
            
            return all_features
        except Exception as e:
            print(f"Error getting multiple track features: {e}")
            return []
    
    def extract_track_id_from_url(self, url: str) -> Optional[str]:
        """
        Extract track ID from Spotify URL.
        
        Args:
            url: Spotify track URL
            
        Returns:
            Track ID or None if invalid
        """
        try:
            if 'spotify.com/track/' in url:
                track_id = url.split('track/')[1].split('?')[0]
                return track_id
            return None
        except:
            return None
    
    def get_genre_info(self, artist_id: str) -> List[str]:
        """
        Get genres for an artist.
        
        Args:
            artist_id: Spotify artist ID
            
        Returns:
            List of genres
        """
        try:
            artist = self.sp.artist(artist_id)
            return artist['genres']
        except Exception as e:
            print(f"Error getting artist genres: {e}")
            return [] 