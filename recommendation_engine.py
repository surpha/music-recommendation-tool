import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances
from sklearn.decomposition import PCA
from typing import List, Dict, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

class RecommendationEngine:
    def __init__(self):
        """Initialize the recommendation engine."""
        self.scaler = StandardScaler()
        self.pca = PCA(n_components=0.95)  # Keep 95% of variance
        self.feature_columns = [
            'danceability', 'energy', 'valence', 'tempo', 'loudness',
            'acousticness', 'instrumentalness', 'liveness', 'speechiness',
            'key', 'mode', 'time_signature'
        ]
        self.numeric_features = [
            'danceability', 'energy', 'valence', 'tempo', 'loudness',
            'acousticness', 'instrumentalness', 'liveness', 'speechiness'
        ]
        self.categorical_features = ['key', 'mode', 'time_signature']
        
        # Feature importance weights for better recommendations
        self.feature_weights = {
            'danceability': 1.2,    # Higher weight for danceability
            'energy': 1.1,          # Important for mood matching
            'valence': 1.3,         # Very important for mood
            'tempo': 0.8,           # Less important but still relevant
            'loudness': 0.6,        # Less important
            'acousticness': 1.0,    # Important for genre matching
            'instrumentalness': 0.9, # Important for style
            'liveness': 0.7,        # Less important
            'speechiness': 0.8      # Important for vocal vs instrumental
        }
    
    def prepare_features(self, tracks_data: List[Dict]) -> pd.DataFrame:
        """
        Prepare and normalize audio features for analysis.
        
        Args:
            tracks_data: List of track dictionaries with audio features
            
        Returns:
            DataFrame with prepared features
        """
        if not tracks_data:
            return pd.DataFrame()
        
        # Convert to DataFrame
        df = pd.DataFrame(tracks_data)
        
        # Handle missing values
        for col in self.numeric_features:
            if col in df.columns:
                df[col] = df[col].fillna(df[col].median())
        
        # Normalize numeric features
        if len(df) > 1:
            df[self.numeric_features] = self.scaler.fit_transform(df[self.numeric_features])
        
        return df
    
    def calculate_similarity_matrix(self, df: pd.DataFrame, method: str = 'cosine') -> np.ndarray:
        """
        Calculate similarity matrix between all tracks.
        
        Args:
            df: DataFrame with audio features
            method: Similarity method ('cosine' or 'euclidean')
            
        Returns:
            Similarity matrix
        """
        if df.empty or len(df) < 2:
            return np.array([])
        
        # Use only numeric features for similarity calculation
        features = df[self.numeric_features].values
        
        if method == 'cosine':
            return cosine_similarity(features)
        elif method == 'euclidean':
            # Convert distance to similarity (1 / (1 + distance))
            distances = euclidean_distances(features)
            return 1 / (1 + distances)
        else:
            raise ValueError("Method must be 'cosine' or 'euclidean'")
    
    def find_similar_tracks(self, 
                          target_track: Dict, 
                          candidate_tracks: List[Dict], 
                          n_recommendations: int = 10,
                          similarity_method: str = 'cosine') -> List[Tuple[Dict, float]]:
        """
        Find similar tracks based on audio features.
        
        Args:
            target_track: The reference track
            candidate_tracks: List of tracks to compare against
            n_recommendations: Number of recommendations to return
            similarity_method: Method for calculating similarity
            
        Returns:
            List of tuples (track, similarity_score)
        """
        if not candidate_tracks:
            return []
        
        # Prepare data
        all_tracks = [target_track] + candidate_tracks
        df = self.prepare_features(all_tracks)
        
        if df.empty:
            return []
        
        # Calculate similarity matrix
        similarity_matrix = self.calculate_similarity_matrix(df, similarity_method)
        
        if similarity_matrix.size == 0:
            return []
        
        # Get similarities to target track (first row)
        similarities = similarity_matrix[0][1:]  # Exclude self-similarity
        
        # Create list of (track, similarity) tuples
        track_similarities = list(zip(candidate_tracks, similarities))
        
        # Sort by similarity (descending)
        track_similarities.sort(key=lambda x: x[1], reverse=True)
        
        return track_similarities[:n_recommendations]
    
    def get_feature_weights(self) -> Dict[str, float]:
        """
        Get feature importance weights for recommendations.
        
        Returns:
            Dictionary of feature weights
        """
        return self.feature_weights
    
    def weighted_similarity(self, 
                          target_track: Dict, 
                          candidate_tracks: List[Dict], 
                          n_recommendations: int = 10) -> List[Tuple[Dict, float]]:
        """
        Find similar tracks using weighted feature importance.
        
        Args:
            target_track: The reference track
            candidate_tracks: List of tracks to compare against
            n_recommendations: Number of recommendations to return
            
        Returns:
            List of tuples (track, similarity_score)
        """
        if not candidate_tracks:
            return []
        
        weights = self.get_feature_weights()
        similarities = []
        
        target_features = {k: target_track.get(k, 0) for k in self.numeric_features}
        
        for track in candidate_tracks:
            track_features = {k: track.get(k, 0) for k in self.numeric_features}
            
            # Calculate weighted similarity
            weighted_diff = 0
            total_weight = 0
            
            for feature in self.numeric_features:
                if feature in weights:
                    weight = weights[feature]
                    diff = abs(target_features[feature] - track_features[feature])
                    weighted_diff += weight * diff
                    total_weight += weight
            
            if total_weight > 0:
                avg_weighted_diff = weighted_diff / total_weight
                similarity = 1 / (1 + avg_weighted_diff)  # Convert to similarity
            else:
                similarity = 0
            
            similarities.append((track, similarity))
        
        # Sort by similarity (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        return similarities[:n_recommendations]
    
    def feature_based_filtering(self, 
                              target_track: Dict, 
                              candidate_tracks: List[Dict],
                              n_recommendations: int = 10) -> List[Tuple[Dict, float]]:
        """
        Advanced feature-based filtering that considers multiple aspects.
        
        Args:
            target_track: The reference track
            candidate_tracks: List of tracks to compare against
            n_recommendations: Number of recommendations to return
            
        Returns:
            List of tuples (track, similarity_score)
        """
        if not candidate_tracks:
            return []
        
        similarities = []
        target_features = {k: target_track.get(k, 0) for k in self.numeric_features}
        
        for track in candidate_tracks:
            track_features = {k: track.get(k, 0) for k in self.numeric_features}
            
            # Calculate multiple similarity scores
            scores = []
            
            # 1. Overall feature similarity (weighted)
            weighted_score = self._calculate_weighted_score(target_features, track_features)
            scores.append(weighted_score * 0.4)  # 40% weight
            
            # 2. Mood similarity (valence + energy)
            mood_score = self._calculate_mood_similarity(target_features, track_features)
            scores.append(mood_score * 0.3)  # 30% weight
            
            # 3. Style similarity (acousticness + instrumentalness)
            style_score = self._calculate_style_similarity(target_features, track_features)
            scores.append(style_score * 0.2)  # 20% weight
            
            # 4. Tempo compatibility
            tempo_score = self._calculate_tempo_similarity(target_features, track_features)
            scores.append(tempo_score * 0.1)  # 10% weight
            
            # Combine scores
            final_score = sum(scores)
            similarities.append((track, final_score))
        
        # Sort by similarity (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        return similarities[:n_recommendations]
    
    def _calculate_weighted_score(self, target: Dict, candidate: Dict) -> float:
        """Calculate weighted feature similarity."""
        weights = self.get_feature_weights()
        weighted_diff = 0
        total_weight = 0
        
        for feature in self.numeric_features:
            if feature in weights:
                weight = weights[feature]
                diff = abs(target[feature] - candidate[feature])
                weighted_diff += weight * diff
                total_weight += weight
        
        if total_weight > 0:
            avg_diff = weighted_diff / total_weight
            return 1 / (1 + avg_diff)
        return 0
    
    def _calculate_mood_similarity(self, target: Dict, candidate: Dict) -> float:
        """Calculate mood similarity based on valence and energy."""
        valence_diff = abs(target.get('valence', 0) - candidate.get('valence', 0))
        energy_diff = abs(target.get('energy', 0) - candidate.get('energy', 0))
        
        # Mood is more important, so we weight it higher
        mood_diff = (valence_diff * 0.6) + (energy_diff * 0.4)
        return 1 / (1 + mood_diff)
    
    def _calculate_style_similarity(self, target: Dict, candidate: Dict) -> float:
        """Calculate style similarity based on acousticness and instrumentalness."""
        acoustic_diff = abs(target.get('acousticness', 0) - candidate.get('acousticness', 0))
        instrumental_diff = abs(target.get('instrumentalness', 0) - candidate.get('instrumentalness', 0))
        
        style_diff = (acoustic_diff * 0.5) + (instrumental_diff * 0.5)
        return 1 / (1 + style_diff)
    
    def _calculate_tempo_similarity(self, target: Dict, candidate: Dict) -> float:
        """Calculate tempo similarity with some tolerance."""
        target_tempo = target.get('tempo', 120)
        candidate_tempo = candidate.get('tempo', 120)
        
        # Normalize tempo to 0-1 range (assuming max tempo is 200 BPM)
        target_norm = target_tempo / 200
        candidate_norm = candidate_tempo / 200
        
        tempo_diff = abs(target_norm - candidate_norm)
        return 1 / (1 + tempo_diff)
    
    def analyze_feature_differences(self, track1: Dict, track2: Dict) -> Dict[str, float]:
        """
        Analyze differences in audio features between two tracks.
        
        Args:
            track1: First track
            track2: Second track
            
        Returns:
            Dictionary of feature differences
        """
        differences = {}
        
        for feature in self.numeric_features:
            val1 = track1.get(feature, 0)
            val2 = track2.get(feature, 0)
            differences[feature] = abs(val1 - val2)
        
        return differences
    
    def get_feature_summary(self, tracks: List[Dict]) -> Dict[str, Dict]:
        """
        Get statistical summary of audio features across tracks.
        
        Args:
            tracks: List of track dictionaries
            
        Returns:
            Dictionary with feature statistics
        """
        if not tracks:
            return {}
        
        df = pd.DataFrame(tracks)
        summary = {}
        
        for feature in self.numeric_features:
            if feature in df.columns:
                summary[feature] = {
                    'mean': df[feature].mean(),
                    'std': df[feature].std(),
                    'min': df[feature].min(),
                    'max': df[feature].max(),
                    'median': df[feature].median()
                }
        
        return summary
    
    def cluster_tracks(self, tracks: List[Dict], n_clusters: int = 3) -> List[int]:
        """
        Cluster tracks based on audio features using K-means.
        
        Args:
            tracks: List of track dictionaries
            n_clusters: Number of clusters
            
        Returns:
            List of cluster labels
        """
        if not tracks or len(tracks) < n_clusters:
            return [0] * len(tracks)
        
        try:
            from sklearn.cluster import KMeans
            
            df = self.prepare_features(tracks)
            if df.empty:
                return [0] * len(tracks)
            
            features = df[self.numeric_features].values
            
            kmeans = KMeans(n_clusters=min(n_clusters, len(tracks)), random_state=42)
            clusters = kmeans.fit_predict(features)
            
            return clusters.tolist()
        except Exception as e:
            print(f"Error clustering tracks: {e}")
            return [0] * len(tracks)
    
    def get_diversity_score(self, tracks: List[Dict]) -> float:
        """
        Calculate diversity score for a set of tracks.
        
        Args:
            tracks: List of track dictionaries
            
        Returns:
            Diversity score (0-1, higher is more diverse)
        """
        if len(tracks) < 2:
            return 0.0
        
        df = self.prepare_features(tracks)
        if df.empty:
            return 0.0
        
        # Calculate average pairwise distance
        features = df[self.numeric_features].values
        distances = euclidean_distances(features)
        
        # Get upper triangle of distance matrix (excluding diagonal)
        upper_triangle = distances[np.triu_indices(len(distances), k=1)]
        
        if len(upper_triangle) == 0:
            return 0.0
        
        # Normalize by maximum possible distance
        max_possible_distance = np.sqrt(len(self.numeric_features))
        diversity = np.mean(upper_triangle) / max_possible_distance
        
        return min(diversity, 1.0)
    
    def filter_by_feature_ranges(self, 
                               target_track: Dict, 
                               candidate_tracks: List[Dict],
                               tolerance: float = 0.3) -> List[Dict]:
        """
        Filter tracks by feature ranges to ensure they're within acceptable bounds.
        
        Args:
            target_track: Reference track
            candidate_tracks: List of candidate tracks
            tolerance: Acceptable deviation from target features (0-1)
            
        Returns:
            Filtered list of tracks
        """
        if not candidate_tracks:
            return []
        
        filtered_tracks = []
        target_features = {k: target_track.get(k, 0) for k in self.numeric_features}
        
        for track in candidate_tracks:
            track_features = {k: track.get(k, 0) for k in self.numeric_features}
            
            # Check if track is within tolerance for key features
            within_tolerance = True
            
            # Key features to check strictly
            key_features = ['valence', 'energy', 'danceability']
            for feature in key_features:
                if feature in target_features and feature in track_features:
                    diff = abs(target_features[feature] - track_features[feature])
                    if diff > tolerance:
                        within_tolerance = False
                        break
            
            if within_tolerance:
                filtered_tracks.append(track)
        
        return filtered_tracks 