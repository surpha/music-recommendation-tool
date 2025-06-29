# 🎵 Music Recommendation Tool

A powerful music recommendation system that finds similar songs based on **audio features only**, not song names or artists. Built with a beautiful Spotify-inspired interface and advanced machine learning algorithms.

![Music Recommendation Tool](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)
![Spotify API](https://img.shields.io/badge/Spotify-API-1DB954.svg)
![Machine Learning](https://img.shields.io/badge/ML-Scikit--learn-orange.svg)

## ✨ Features

- **🎯 Feature-Based Recommendations**: Analyzes songs purely by audio characteristics (mood, energy, tempo, etc.)
- **🎨 Spotify-Inspired UI**: Beautiful dark theme with green accents matching Spotify's design
- **🧠 Advanced ML Algorithms**: Multiple similarity methods including feature-based filtering
- **📊 Interactive Visualizations**: Radar charts and feature comparisons
- **🎧 Audio Previews**: Listen to song previews directly in the app
- **📱 Responsive Design**: Works perfectly on desktop and mobile
- **⚡ Real-time Analysis**: Instant recommendations with detailed reasoning

## 🎯 How It Works

Unlike traditional recommendation systems that rely on song names, artists, or genres, this tool analyzes the **actual audio characteristics**:

1. **Mood Analysis** (30% weight): Valence (happiness) + Energy
2. **Style Matching** (20% weight): Acousticness + Instrumentalness  
3. **Overall Features** (40% weight): Weighted combination of all audio features
4. **Tempo Compatibility** (10% weight): BPM matching

### Example
- Search for "Bohemian Rhapsody" → Get recommendations like "Stairway to Heaven" (similar mood/style)
- Search for "Happy" by Pharrell → Get other upbeat, positive songs regardless of genre
- Search for "Nothing Else Matters" → Get other slow, acoustic, emotional songs

## 🚀 Quick Start

### 1. Setup Spotify API
1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Create a new app
3. Copy your `CLIENT_ID` and `CLIENT_SECRET`

### 2. Install Dependencies
```bash
git clone https://github.com/yourusername/music-recommendation-tool.git
cd music-recommendation-tool
pip install -r requirements.txt
```

### 3. Configure Environment
Create a `.env` file:
```bash
SPOTIFY_CLIENT_ID=your_client_id_here
SPOTIFY_CLIENT_SECRET=your_client_secret_here
SECRET_KEY=your-secret-key-here
FLASK_DEBUG=False
PORT=8080
```

### 4. Run the Application
```bash
python app.py
```

Open your browser and go to `http://localhost:8080`

## 🎨 Screenshots

### Main Interface
- Spotify-inspired dark theme
- Clean, modern design
- Intuitive search and selection

### Feature Analysis
- Interactive radar charts
- Detailed audio feature breakdowns
- Similarity score explanations

## 🔧 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main dashboard |
| `/search` | POST | Search for songs |
| `/recommendations` | POST | Get song recommendations |
| `/track/<id>` | GET | Get track details |
| `/analyze` | POST | Analyze multiple tracks |
| `/health` | GET | Health check |

## 🧠 Recommendation Methods

### 1. 🎯 Feature-Based (Recommended)
Advanced algorithm that considers:
- **Mood Similarity**: Valence + Energy matching
- **Style Compatibility**: Acousticness + Instrumentalness
- **Overall Feature Match**: Weighted combination
- **Tempo Compatibility**: BPM similarity

### 2. 📊 Cosine Similarity
Mathematical similarity based on feature vectors

### 3. 📏 Euclidean Distance
Distance-based similarity calculation

### 4. ⚖️ Weighted Features
Custom-weighted feature importance

## 🛠️ Technology Stack

### Backend
- **Python 3.9+**: Core programming language
- **Flask**: Web framework
- **Spotipy**: Spotify API wrapper
- **Scikit-learn**: Machine learning algorithms
- **Pandas/NumPy**: Data processing

### Frontend
- **HTML5/CSS3**: Modern web standards
- **JavaScript (ES6+)**: Interactive functionality
- **Bootstrap 5**: Responsive design
- **Plotly.js**: Interactive charts
- **Font Awesome**: Icons

### DevOps
- **GitHub Actions**: CI/CD pipeline
- **Heroku**: Deployment platform
- **Gunicorn**: Production server

## 📁 Project Structure

```
├── app.py                     # Main Flask application
├── spotify_client.py          # Spotify API client
├── recommendation_engine.py   # ML recommendation engine
├── utils.py                   # Utility functions
├── templates/index.html       # Main web interface
├── static/css/style.css       # Spotify-inspired styles
├── static/js/app.js          # Frontend functionality
└── requirements.txt           # Dependencies
```

## 🚀 Deployment

### Heroku
1. Fork this repository
2. Create a new Heroku app
3. Add environment variables in Heroku dashboard
4. Deploy automatically via GitHub Actions

### Local Development
```bash
# Install development dependencies
pip install -r requirements.txt
pip install flake8 black

# Run linting
flake8 .
black .

# Run tests
python -c "from app import app; print('App loaded successfully')"
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Spotify**: For providing the amazing API and audio features
- **Scikit-learn**: For powerful machine learning tools
- **Bootstrap**: For responsive design framework
- **Plotly**: For beautiful interactive visualizations

## 📞 Support

If you have any questions or need help:
- Open an issue on GitHub
- Check the documentation
- Review the code comments

---

**Made with ❤️ and 🎵 by Suraj**

*This project is not affiliated with Spotify Inc.* 