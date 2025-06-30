// Music Recommendation App JavaScript
class MusicRecommendationApp {
    constructor() {
        this.currentTrack = null;
        this.recommendations = [];
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.showSearchSection();
        this.loadRecommendationMethods();
    }

    setupEventListeners() {
        // Search form
        const searchForm = document.getElementById('searchForm');
        if (searchForm) {
            searchForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleSearch();
            });
        }

        // Recommendation form
        const recommendForm = document.getElementById('recommendForm');
        if (recommendForm) {
            recommendForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleRecommendation();
            });
        }

        // Method selection
        const methodSelect = document.getElementById('methodSelect');
        if (methodSelect) {
            methodSelect.addEventListener('change', () => {
                this.updateMethodDescription();
            });
        }

        // Navigation
        const searchLink = document.getElementById('searchLink');
        if (searchLink) {
            searchLink.addEventListener('click', (e) => {
                e.preventDefault();
                this.showSearchSection();
            });
        }

        const recommendationsLink = document.getElementById('recommendationsLink');
        if (recommendationsLink) {
            recommendationsLink.addEventListener('click', (e) => {
                e.preventDefault();
                this.showRecommendationsSection();
            });
        }
    }

    async handleSearch() {
        const searchInput = document.getElementById('searchInput');
        const query = searchInput.value.trim();

        if (!query) {
            this.showError('Please enter a song name to search for.');
            return;
        }

        this.showLoading('Searching for songs...');
        
        try {
            const response = await fetch('/search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ query })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Search failed');
            }

            // Display all filtered results
            this.displaySearchResults(data.songs);
            this.lastSearchQuery = query; // Save for recommendations
            
        } catch (error) {
            console.error('Search error:', error);
            this.showError(error.message || 'An error occurred while searching.');
        } finally {
            this.hideLoading();
        }
    }

    displaySearchResults(songs) {
        const resultsContainer = document.getElementById('searchResults');
        if (!resultsContainer) return;

        if (!songs || songs.length === 0) {
            resultsContainer.innerHTML = '<p class="text-muted">No songs found. Try a different search term.</p>';
            return;
        }

        const songsHTML = songs.map((song, index) => `
            <div class="col-md-6 col-lg-4 mb-3">
                <div class="card h-100 song-card" data-track-id="${song.id}">
                    <div class="card-body d-flex">
                        <div class="flex-shrink-0 me-3">
                            <img src="${song.image_url || '/static/images/default-album.png'}" 
                                 alt="${song.name}" 
                                 class="album-cover" 
                                 onerror="this.src='/static/images/default-album.png'">
                        </div>
                        <div class="flex-grow-1">
                            <h6 class="card-title mb-1">${this.escapeHtml(song.name)}</h6>
                            <p class="card-text text-muted mb-2">${this.escapeHtml(song.artist)}</p>
                            <p class="card-text small text-muted mb-2">${this.escapeHtml(song.album)}</p>
                            <div class="d-flex justify-content-between align-items-center mb-2">
                                <span class="badge bg-secondary">#${index + 1}</span>
                            </div>
                            <button class="btn btn-success btn-sm w-100" onclick="app.selectTrack('${song.id}')">
                                <i class="fas fa-music me-1"></i>Get Recommendations
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `).join('');

        resultsContainer.innerHTML = `
            <div class="mb-3">
                <div class="alert alert-info">
                    <i class="fas fa-info-circle me-2"></i>
                    <strong>Filtered Results:</strong> Showing ${songs.length} songs that don't contain "${this.lastSearchQuery}" in their name.
                </div>
            </div>
            <div class="row">
                ${songsHTML}
            </div>
        `;
    }

    selectTrack(trackId) {
        // Find the selected track in search results
        const trackCard = document.querySelector(`[data-track-id="${trackId}"]`);
        if (trackCard) {
            // Remove previous selection
            document.querySelectorAll('.song-card').forEach(card => {
                card.classList.remove('selected');
            });
            
            // Add selection to current card
            trackCard.classList.add('selected');
        }

        this.currentTrack = trackId;
        this.showRecommendationsSection();
        
        // Update the hidden input
        const trackIdInput = document.getElementById('trackIdInput');
        if (trackIdInput) {
            trackIdInput.value = trackId;
        }
    }

    async handleRecommendation() {
        if (!this.currentTrack) {
            this.showError('Please select a track first.');
            return;
        }

        const methodSelect = document.getElementById('methodSelect');
        const method = methodSelect ? methodSelect.value : 'feature_based';

        this.showLoading('Finding similar songs...');
        
        try {
            const response = await fetch('/recommend', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    track_id: this.currentTrack,
                    method: method,
                    input_track_name: this.lastSearchQuery || '' // Pass original search query
                })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Failed to get recommendations');
            }

            this.displayRecommendations(data);
            
        } catch (error) {
            console.error('Recommendation error:', error);
            this.showError(error.message || 'An error occurred while getting recommendations.');
        } finally {
            this.hideLoading();
        }
    }

    displayRecommendations(data) {
        const { target_track, recommendations, method_used, total_candidates } = data;
        
        this.recommendations = recommendations;
        
        // Display target track
        this.displayTargetTrack(target_track);
        
        // Display recommendations
        this.displayRecommendationsList(recommendations, method_used, total_candidates);
        
        // Show recommendations section
        this.showRecommendationsSection();
    }

    displayTargetTrack(targetTrack) {
        const targetContainer = document.getElementById('targetTrack');
        if (!targetContainer) return;

        targetContainer.innerHTML = `
            <div class="card">
                <div class="card-body">
                    <h5 class="card-title">Based on:</h5>
                    <div class="d-flex align-items-center">
                        <div class="flex-shrink-0 me-3">
                            <img src="${targetTrack.image_url || '/static/images/default-album.png'}" 
                                 alt="${targetTrack.name}" 
                                 class="album-cover" 
                                 onerror="this.src='/static/images/default-album.png'">
                        </div>
                        <div class="flex-grow-1">
                            <h6 class="mb-1">${this.escapeHtml(targetTrack.name)}</h6>
                            <p class="text-muted mb-1">${this.escapeHtml(targetTrack.artist)}</p>
                            <p class="text-muted small mb-0">${this.escapeHtml(targetTrack.album)}</p>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    displayRecommendationsList(recommendations, methodUsed, totalCandidates) {
        const recommendationsContainer = document.getElementById('recommendationsList');
        if (!recommendationsContainer) return;

        if (!recommendations || recommendations.length === 0) {
            recommendationsContainer.innerHTML = '<p class="text-muted">No recommendations found.</p>';
            return;
        }

        // Create method info
        const methodInfo = this.getMethodInfo(methodUsed);
        
        const recommendationsHTML = recommendations.map((track, index) => `
            <div class="col-md-6 col-lg-4 mb-3">
                <div class="card h-100 recommendation-card">
                    <div class="card-body">
                        <div class="d-flex align-items-start">
                            <div class="flex-shrink-0 me-3">
                                <img src="${track.image_url || '/static/images/default-album.png'}" 
                                     alt="${track.name}" 
                                     class="album-cover" 
                                     onerror="this.src='/static/images/default-album.png'">
                            </div>
                            <div class="flex-grow-1">
                                <h6 class="card-title mb-1">${this.escapeHtml(track.name)}</h6>
                                <p class="card-text text-muted mb-1">${this.escapeHtml(track.artist)}</p>
                                <p class="card-text small text-muted mb-2">${this.escapeHtml(track.album)}</p>
                                
                                <div class="d-flex justify-content-between align-items-center mb-2">
                                    <span class="badge bg-success">Similarity: ${track.similarity_score}%</span>
                                    <span class="badge bg-secondary">#${index + 1}</span>
                                </div>
                                
                                <div class="btn-group btn-group-sm w-100" role="group">
                                    ${track.preview_url ? 
                                        `<button class="btn btn-outline-primary" onclick="app.playPreview('${track.preview_url}')">
                                            <i class="fas fa-play"></i> Preview
                                        </button>` : 
                                        '<button class="btn btn-outline-secondary" disabled>No Preview</button>'
                                    }
                                    ${track.external_url ? 
                                        `<a href="${track.external_url}" target="_blank" class="btn btn-outline-success">
                                            <i class="fab fa-spotify"></i> Open
                                        </a>` : 
                                        '<button class="btn btn-outline-secondary" disabled>No Link</button>'
                                    }
                                </div>
                            </div>
                        </div>
                        
                        <!-- Audio Features Visualization -->
                        <div class="mt-3">
                            <small class="text-muted">Audio Features:</small>
                            <div class="audio-features mt-1">
                                ${this.createAudioFeaturesBars(track.audio_features)}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `).join('');

        recommendationsContainer.innerHTML = `
            <div class="mb-3">
                <div class="alert alert-info">
                    <i class="fas fa-info-circle me-2"></i>
                    <strong>${methodInfo.name}</strong>: ${methodInfo.description}
                    <br>
                    <small class="text-muted">
                        Found ${recommendations.length} recommendations from ${totalCandidates} candidates 
                        (duplicates filtered out, sorted by similarity)
                    </small>
                </div>
            </div>
            <div class="row">
                ${recommendationsHTML}
            </div>
        `;
    }

    createAudioFeaturesBars(features) {
        const featureNames = {
            'danceability': 'Dance',
            'energy': 'Energy',
            'valence': 'Mood',
            'acousticness': 'Acoustic',
            'instrumentalness': 'Instrumental',
            'liveness': 'Live',
            'speechiness': 'Speech'
        };

        return Object.entries(features).map(([key, value]) => {
            if (key in featureNames) {
                const percentage = Math.round(value * 100);
                return `
                    <div class="feature-bar mb-1">
                        <div class="d-flex justify-content-between">
                            <small>${featureNames[key]}</small>
                            <small>${percentage}%</small>
                        </div>
                        <div class="progress" style="height: 4px;">
                            <div class="progress-bar bg-success" style="width: ${percentage}%"></div>
                        </div>
                    </div>
                `;
            }
            return '';
        }).join('');
    }

    getMethodInfo(method) {
        const methods = {
            'feature_based': {
                name: 'Feature-Based Filtering',
                description: 'Advanced analysis considering mood, style, tempo, and overall audio features with weighted importance.'
            },
            'cosine': {
                name: 'Cosine Similarity',
                description: 'Measures similarity based on the cosine of the angle between audio feature vectors.'
            },
            'euclidean': {
                name: 'Euclidean Distance',
                description: 'Measures similarity based on the straight-line distance between audio feature points.'
            },
            'weighted': {
                name: 'Weighted Similarity',
                description: 'Uses feature importance weights to prioritize certain audio characteristics.'
            }
        };
        
        return methods[method] || methods['feature_based'];
    }

    loadRecommendationMethods() {
        const methodSelect = document.getElementById('methodSelect');
        if (!methodSelect) return;

        const methods = [
            { value: 'feature_based', label: 'Feature-Based (Recommended)' },
            { value: 'cosine', label: 'Cosine Similarity' },
            { value: 'euclidean', label: 'Euclidean Distance' },
            { value: 'weighted', label: 'Weighted Similarity' }
        ];

        methodSelect.innerHTML = methods.map(method => 
            `<option value="${method.value}">${method.label}</option>`
        ).join('');

        this.updateMethodDescription();
    }

    updateMethodDescription() {
        const methodSelect = document.getElementById('methodSelect');
        const methodDescription = document.getElementById('methodDescription');
        
        if (!methodSelect || !methodDescription) return;

        const method = methodSelect.value;
        const methodInfo = this.getMethodInfo(method);
        
        methodDescription.textContent = methodInfo.description;
    }

    playPreview(previewUrl) {
        // Stop any currently playing audio
        const currentAudio = document.querySelector('audio');
        if (currentAudio) {
            currentAudio.pause();
            currentAudio.remove();
        }

        // Create and play new audio
        const audio = new Audio(previewUrl);
        audio.volume = 0.5;
        audio.play().catch(error => {
            console.error('Error playing preview:', error);
            this.showError('Could not play audio preview.');
        });

        // Remove audio element when finished
        audio.addEventListener('ended', () => {
            audio.remove();
        });
    }

    showSearchSection() {
        this.hideAllSections();
        const searchSection = document.getElementById('searchSection');
        if (searchSection) {
            searchSection.style.display = 'block';
        }
        this.updateNavigation('search');
    }

    showRecommendationsSection() {
        this.hideAllSections();
        const recommendationsSection = document.getElementById('recommendationsSection');
        if (recommendationsSection) {
            recommendationsSection.style.display = 'block';
        }
        this.updateNavigation('recommendations');
    }

    hideAllSections() {
        const sections = ['searchSection', 'recommendationsSection'];
        sections.forEach(sectionId => {
            const section = document.getElementById(sectionId);
            if (section) {
                section.style.display = 'none';
            }
        });
    }

    updateNavigation(activeSection) {
        // Update navigation links
        const searchLink = document.getElementById('searchLink');
        const recommendationsLink = document.getElementById('recommendationsLink');
        
        if (searchLink) {
            searchLink.classList.toggle('active', activeSection === 'search');
        }
        if (recommendationsLink) {
            recommendationsLink.classList.toggle('active', activeSection === 'recommendations');
        }
    }

    showLoading(message = 'Loading...') {
        const loadingDiv = document.getElementById('loading');
        if (loadingDiv) {
            loadingDiv.innerHTML = `
                <div class="text-center">
                    <div class="spinner-border text-success" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <p class="mt-2">${message}</p>
                </div>
            `;
            loadingDiv.style.display = 'block';
        }
    }

    hideLoading() {
        const loadingDiv = document.getElementById('loading');
        if (loadingDiv) {
            loadingDiv.style.display = 'none';
        }
    }

    showError(message) {
        const alertContainer = document.getElementById('alertContainer');
        if (alertContainer) {
            alertContainer.innerHTML = `
                <div class="alert alert-danger alert-dismissible fade show" role="alert">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    ${this.escapeHtml(message)}
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>
            `;
            alertContainer.style.display = 'block';
            
            // Auto-hide after 5 seconds
            setTimeout(() => {
                alertContainer.style.display = 'none';
            }, 5000);
        }
    }

    showSuccess(message) {
        const alertContainer = document.getElementById('alertContainer');
        if (alertContainer) {
            alertContainer.innerHTML = `
                <div class="alert alert-success alert-dismissible fade show" role="alert">
                    <i class="fas fa-check-circle me-2"></i>
                    ${this.escapeHtml(message)}
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>
            `;
            alertContainer.style.display = 'block';
            
            // Auto-hide after 3 seconds
            setTimeout(() => {
                alertContainer.style.display = 'none';
            }, 3000);
        }
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new MusicRecommendationApp();
}); 