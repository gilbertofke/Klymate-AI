# 🌱 Klymate AI

**AI-Powered Carbon Footprint Tracker with Personalized Coaching**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![TiDB](https://img.shields.io/badge/TiDB-Cloud-orange.svg)](https://tidbcloud.com/)

Klymate AI is a comprehensive carbon footprint tracking platform that combines habit monitoring with AI-powered coaching to help users reduce their environmental impact. Built with modern technologies and designed for scalability, it provides personalized recommendations, gamification features, and detailed analytics to make sustainability engaging and achievable.

## ✨ Features

### 🎯 **Smart Habit Tracking**
- **Comprehensive Categories**: Track transport, diet, energy usage, and lifestyle choices
- **Real-time Calculations**: Instant carbon footprint calculations for every logged activity
- **Historical Analytics**: Detailed insights into your environmental impact over time

### 🤖 **AI-Powered Coaching**
- **Personalized Recommendations**: AI coach provides tailored advice based on your habits
- **Contextual Conversations**: Natural language interactions with memory of past discussions
- **Smart Insights**: Vector-powered semantic search for relevant tips and suggestions

### 🏆 **Gamification & Motivation**
- **Achievement System**: Earn badges for reaching sustainability milestones
- **Streak Tracking**: Maintain daily and weekly eco-friendly habits
- **Leaderboards**: Friendly competition with eco-scores and rankings
- **Challenge Participation**: Join community challenges for extra motivation

### 📊 **Advanced Analytics**
- **Dashboard Insights**: Visual representation of your carbon footprint trends
- **Goal Tracking**: Set and monitor personalized reduction targets
- **Comparative Analysis**: See how your efforts stack up against benchmarks

## 🏗️ Architecture

Klymate AI is built with a modern, scalable architecture:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Database      │
│   (React/Vue)   │◄──►│   (FastAPI)     │◄──►│   (TiDB Cloud)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐    ┌─────────────────┐
                    │   AI Services   │    │   Caching       │
                    │   (LangChain)   │    │   (Redis)       │
                    └─────────────────┘    └─────────────────┘
```

### **Technology Stack**

**Backend**
- **FastAPI**: High-performance Python web framework
- **SQLAlchemy**: Async ORM for database operations
- **TiDB Cloud**: Distributed SQL database with vector capabilities
- **LangChain**: AI orchestration and conversation management
- **OpenAI**: GPT models for intelligent coaching
- **Redis**: Caching and session management
- **Firebase**: Authentication and user management

**Infrastructure**
- **Docker**: Containerized deployment
- **GitHub Actions**: CI/CD pipeline
- **Cloud Deployment**: Railway/Render/AWS support

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 16+ (for frontend)
- Docker (optional)
- TiDB Cloud account
- OpenAI API key
- Firebase project

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/klymate-ai.git
   cd klymate-ai
   ```

2. **Set up the backend environment**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Run the development server**
   ```bash
   python main.py
   ```

The API will be available at `http://localhost:8000` with interactive docs at `/docs`.

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

## 📖 API Documentation

### Authentication
```http
POST /auth/register    # User registration
POST /auth/login       # User login
GET  /auth/profile     # Get user profile
```

### Habit Tracking
```http
POST /habits/log       # Log a new habit
GET  /habits/history   # Get habit history
GET  /habits/stats     # Get user statistics
```

### AI Coaching
```http
POST /ai/chat          # Chat with AI coach
GET  /ai/suggestions   # Get personalized tips
```

### Gamification
```http
GET  /gamification/badges      # Get user badges
GET  /gamification/leaderboard # Get leaderboard
```

Full API documentation is available at `/docs` when running the server.

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=.

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
pytest tests/e2e/
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🌟 Acknowledgments

- **TiDB Cloud** for providing scalable database infrastructure
- **OpenAI** for powering our AI coaching capabilities
- **FastAPI** community for the excellent framework
- **LangChain** for AI orchestration tools

## 📞 Support

- **Documentation**: [docs.klymate-ai.com](https://docs.klymate-ai.com)
- **Issues**: [GitHub Issues](https://github.com/your-org/klymate-ai/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/klymate-ai/discussions)
- **Email**: support@klymate-ai.com

---

**Made with 💚 for a sustainable future**
