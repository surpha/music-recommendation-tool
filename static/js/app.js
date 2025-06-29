// Music Recommendation Tool - Frontend JavaScript

class MusicRecommendationApp {
    constructor() {
        this.currentTrack = null;
        this.recommendations = [];
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.showWelcomeMessage();
    }

    setupEventListeners() {
        // Search input enter key
        document.getElementById('searchInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.searchTracks();
            }
        });

        // Search method change
        document.getElementById('searchMethod').addEventListener('change', () => {
            if (this.currentTrack) {
                this.getRecommendations();
            }
        });
    }

    showWelcomeMessage() {
        const searchInput = document.getElementById('searchInput');
        searchInput.placeholder = "Try: 'Bohemian Rhapsody Queen' or paste a Spotify URL...";
    }

    async searchTracks() {
        const query = document.getElementById('searchInput').value.trim();
        
        if (!query) {
            this.showAlert('Please enter a song name, artist, or Spotify URL', 'warning');
            return;
        }

        this.showLoading(true);
        this.hideAllSections();

        try {
            const response = await fetch('/search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ query: query })
            });

            const data = await response.json();

            if (response.ok) {
                this.displaySearchResults(data.tracks);
                this.showSection('searchResults');
            } else {
                this.showAlert(data.error || 'Search failed', 'danger');
            }
        } catch (error) {
            console.error('Search error:', error);
            this.showAlert('Network error. Please try again.', 'danger');
        } finally {
            this.showLoading(false);
        }
    }

    displaySearchResults(tracks) {
        const tracksList = document.getElementById('tracksList');
        tracksList.innerHTML = '';

        tracks.forEach((track, index) => {
            const trackCard = this.createTrackCard(track, 'search');
            tracksList.appendChild(trackCard);
        });
    }

    createTrackCard(track, type = 'search') {
        const col = document.createElement('div');
        col.className = 'col-md-6 col-lg-4 mb-3';
        
        const cardClass = type === 'search' ? 'track-card' : 'track-card recommendation';
        
        col.innerHTML = `
            <div class="${cardClass} fade-in" data-track-id="${track.id}">
                <div class="d-flex justify-content-between align-items-start mb-2">
                    <h6 class="mb-1 fw-bold">${this.escapeHtml(track.name)}</h6>
                    <span class="badge bg-secondary">${track.popularity || 0}%</span>
                </div>
                <p class="text-muted mb-2">
                    <i class="fas fa-user"></i> ${this.escapeHtml(track.artist)}
                </p>
                <p class="text-muted small mb-3">
                    <i class="fas fa-compact-disc"></i> ${this.escapeHtml(track.album)}
                </p>
                
                ${track.preview_url ? `
                    <audio controls class="audio-player mb-3">
                        <source src="${track.preview_url}" type="audio/mpeg">
                        Your browser does not support the audio element.
                    </audio>
                ` : ''}
                
                <div class="d-flex gap-2">
                    ${type === 'search' ? `
                        <button class="btn btn-primary btn-sm" onclick="app.selectTrack('${track.id}')">
                            <i class="fas fa-star"></i> Select
                        </button>
                    ` : `
                        <span class="similarity-badge ${this.getSimilarityClass(track.similarity_score)}">
                            ${track.similarity_percentage || 'N/A'}
                        </span>
                    `}
                    
                    <a href="${track.external_url}" target="_blank" class="btn btn-outline-secondary btn-sm">
                        <i class="fab fa-spotify"></i> Open
                    </a>
                </div>
                
                ${type === 'recommendation' && track.reasoning ? `
                    <div class="mt-2">
                        <small class="text-muted">
                            <i class="fas fa-lightbulb"></i> 
                            ${track.reasoning.slice(0, 2).join(', ')}
                        </small>
                    </div>
                ` : ''}
            </div>
        `;

        return col;
    }

    async selectTrack(trackId) {
        this.showLoading(true);
        
        try {
            const response = await fetch(`/track/${trackId}`);
            const track = await response.json();
            
            if (response.ok) {
                this.currentTrack = track;
                this.displayTargetTrack(track);
                this.showSection('targetTrackInfo');
                await this.getRecommendations();
            } else {
                this.showAlert('Failed to get track details', 'danger');
            }
        } catch (error) {
            console.error('Error selecting track:', error);
            this.showAlert('Network error. Please try again.', 'danger');
        } finally {
            this.showLoading(false);
        }
    }

    displayTargetTrack(track) {
        const targetDetails = document.getElementById('targetTrackDetails');
        
        targetDetails.innerHTML = `
            <div class="row">
                <div class="col-md-8">
                    <h4 class="mb-3">
                        <i class="fas fa-music"></i> ${this.escapeHtml(track.name)}
                    </h4>
                    <p class="lead mb-2">
                        <i class="fas fa-user"></i> ${this.escapeHtml(track.artist)}
                    </p>
                    <p class="text-muted mb-3">
                        <i class="fas fa-compact-disc"></i> ${this.escapeHtml(track.album)}
                    </p>
                    
                    ${track.preview_url ? `
                        <audio controls class="audio-player mb-3">
                            <source src="${track.preview_url}" type="audio/mpeg">
                            Your browser does not support the audio element.
                        </audio>
                    ` : ''}
                    
                    <a href="${track.external_url}" target="_blank" class="btn btn-success">
                        <i class="fab fa-spotify"></i> Open in Spotify
                    </a>
                </div>
                <div class="col-md-4">
                    <div class="text-center">
                        <div class="display-4 text-primary mb-2">${track.popularity}%</div>
                        <div class="text-muted">Popularity</div>
                    </div>
                </div>
            </div>
            
            <hr class="my-4">
            
            <h5 class="mb-3">
                <i class="fas fa-chart-bar"></i> Audio Features
            </h5>
            <div class="row">
                ${this.createFeatureBars(track.features)}
            </div>
        `;
    }

    createFeatureBars(features) {
        const featureNames = {
            'danceability': 'Danceability',
            'energy': 'Energy',
            'valence': 'Valence',
            'acousticness': 'Acousticness',
            'instrumentalness': 'Instrumentalness',
            'liveness': 'Liveness',
            'speechiness': 'Speechiness'
        };

        return Object.entries(featureNames).map(([key, name]) => {
            const feature = features[key];
            const percentage = Math.round(feature.value * 100);
            const level = percentage > 66 ? 'high' : percentage > 33 ? 'medium' : 'low';
            
            return `
                <div class="col-md-6 col-lg-4 mb-3">
                    <div class="d-flex justify-content-between mb-1">
                        <small class="fw-bold">${name}</small>
                        <small class="text-muted">${percentage}%</small>
                    </div>
                    <div class="feature-bar">
                        <div class="feature-fill ${level}" style="width: ${percentage}%"></div>
                    </div>
                    <small class="text-muted">${feature.description}</small>
                </div>
            `;
        }).join('');
    }

    async getRecommendations() {
        if (!this.currentTrack) return;

        this.showLoading(true);
        
        try {
            const method = document.getElementById('searchMethod').value;
            
            const response = await fetch('/recommendations', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    track_id: this.currentTrack.id,
                    method: method,
                    limit: 15
                })
            });

            const data = await response.json();
            
            if (response.ok) {
                this.recommendations = data.recommendations;
                this.displayRecommendations(data.recommendations);
                this.showSection('recommendationsSection');
                this.createFeatureComparisonChart(data.target_track, data.recommendations);
            } else {
                this.showAlert(data.error || 'Failed to get recommendations', 'danger');
            }
        } catch (error) {
            console.error('Error getting recommendations:', error);
            this.showAlert('Network error. Please try again.', 'danger');
        } finally {
            this.showLoading(false);
        }
    }

    displayRecommendations(recommendations) {
        const recommendationsList = document.getElementById('recommendationsList');
        recommendationsList.innerHTML = '';

        recommendations.forEach((track, index) => {
            const trackCard = this.createTrackCard(track, 'recommendation');
            trackCard.querySelector('.track-card').classList.add('slide-in');
            recommendationsList.appendChild(trackCard);
        });
    }

    createFeatureComparisonChart(targetTrack, recommendations) {
        const featureCharts = document.getElementById('featureCharts');
        featureCharts.innerHTML = '';

        // Create radar chart for feature comparison
        const features = ['danceability', 'energy', 'valence', 'acousticness', 'instrumentalness', 'liveness', 'speechiness'];
        const featureLabels = ['Danceability', 'Energy', 'Valence', 'Acousticness', 'Instrumentalness', 'Liveness', 'Speechiness'];

        const targetValues = features.map(f => targetTrack.features[f].value);
        const avgValues = features.map(f => {
            const values = recommendations.map(r => r[f] || 0);
            return values.reduce((a, b) => a + b, 0) / values.length;
        });

        const data = [
            {
                type: 'scatterpolar',
                r: targetValues,
                theta: featureLabels,
                fill: 'toself',
                name: 'Selected Track',
                line: { color: '#007bff' },
                fillcolor: 'rgba(0, 123, 255, 0.1)'
            },
            {
                type: 'scatterpolar',
                r: avgValues,
                theta: featureLabels,
                fill: 'toself',
                name: 'Average of Recommendations',
                line: { color: '#28a745' },
                fillcolor: 'rgba(40, 167, 69, 0.1)'
            }
        ];

        const layout = {
            polar: {
                radialaxis: {
                    visible: true,
                    range: [0, 1]
                }
            },
            showlegend: true,
            title: 'Audio Feature Comparison',
            height: 500
        };

        Plotly.newPlot(featureCharts, data, layout, {responsive: true});

        this.showSection('featureAnalysis');
    }

    getSimilarityClass(score) {
        if (score >= 0.9) return 'similarity-excellent';
        if (score >= 0.8) return 'similarity-good';
        if (score >= 0.7) return 'similarity-moderate';
        return 'similarity-weak';
    }

    showLoading(show) {
        const spinner = document.getElementById('loadingSpinner');
        if (show) {
            spinner.classList.remove('d-none');
        } else {
            spinner.classList.add('d-none');
        }
    }

    hideAllSections() {
        const sections = ['searchResults', 'targetTrackInfo', 'recommendationsSection', 'featureAnalysis'];
        sections.forEach(section => {
            document.getElementById(section).classList.add('d-none');
        });
    }

    showSection(sectionId) {
        document.getElementById(sectionId).classList.remove('d-none');
    }

    showAlert(message, type = 'info') {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        const container = document.querySelector('.container');
        container.insertBefore(alertDiv, container.firstChild);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize the app when the page loads
let app;
document.addEventListener('DOMContentLoaded', () => {
    app = new MusicRecommendationApp();
});

// Global function for track selection (called from HTML)
function selectTrack(trackId) {
    if (app) {
        app.selectTrack(trackId);
    }
}

// Global function for search (called from HTML)
function searchTracks() {
    if (app) {
        app.searchTracks();
    }
} 