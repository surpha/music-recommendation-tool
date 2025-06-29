# Project Structure

```
music-recommendation-tool/
├── .github/
│   └── workflows/
│       ├── ci.yml              # Continuous Integration workflow
│       └── deploy.yml          # Deployment workflow
├── static/
│   ├── css/
│   │   └── style.css          # Spotify-inspired CSS styles
│   └── js/
│       └── app.js             # Frontend JavaScript
├── templates/
│   └── index.html             # Main HTML template
├── app.py                     # Main Flask application
├── spotify_client.py          # Spotify API client
├── recommendation_engine.py   # ML-based recommendation engine
├── utils.py                   # Utility functions
├── requirements.txt           # Python dependencies
├── Procfile                   # Heroku deployment config
├── .gitignore                 # Git ignore rules
├── README.md                  # Project documentation
├── PROJECT_STRUCTURE.md       # This file
└── env_example.txt           # Environment variables template
```

## Key Components

### Backend (Python/Flask)
- **`app.py`**: Main Flask application with API endpoints
- **`spotify_client.py`**: Handles Spotify API authentication and requests
- **`recommendation_engine.py`**: Machine learning engine for song similarity
- **`utils.py`**: Helper functions for data formatting and processing

### Frontend (HTML/CSS/JavaScript)
- **`templates/index.html`**: Main web interface
- **`static/css/style.css`**: Spotify-inspired dark theme
- **`static/js/app.js`**: Interactive frontend functionality

### Configuration
- **`requirements.txt`**: Python package dependencies
- **`Procfile`**: Heroku deployment configuration
- **`.env`**: Environment variables (not in repo)
- **`env_example.txt`**: Template for environment variables

### CI/CD
- **`.github/workflows/ci.yml`**: Automated testing
- **`.github/workflows/deploy.yml`**: Automated deployment 