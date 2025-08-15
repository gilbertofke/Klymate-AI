# 🌱 Klymate AI

**AI-Powered Carbon Footprint Tracker with Personalized Coaching**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![TiDB](https://img.shields.io/badge/TiDB-Cloud-orange.svg)](https://tidbcloud.com/)

Klymate AI is a comprehensive carbon footprint tracking platform that combines habit monitoring with AI-powered coaching to help users reduce their environmental impact. Built with modern technologies and designed for scalability, it provides personalized recommendations, gamification features, **real carbon credits with monetary value**, and detailed analytics to make sustainability both engaging and financially rewarding.

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

### � **Carabon Credits System**
- **Earn Real Credits**: Get Klymate Credits (KC) for verified carbon reduction activities
- **Monetary Conversion**: Convert credits to cash rewards or carbon offset certificates
- **Transparent Verification**: Multi-level verification with blockchain-style transaction records
- **Market Integration**: Real-time carbon market rates and corporate partnership opportunities
- **Multiple Redemption Options**: Cash out, purchase carbon offsets, or donate to climate causes

### 📊 **Advanced Analytics**
- **Dashboard Insights**: Visual representation of your carbon footprint trends
- **Goal Tracking**: Set and monitor personalized reduction targets
- **Comparative Analysis**: See how your efforts stack up against benchmarks
- **Credit Analytics**: Track your carbon credit earnings and redemption history

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

### Project Structure

```
klymate-ai/
├── backend/                    # FastAPI backend application
│   ├── app/                   # Core application code
│   │   ├── api/v1/endpoints/  # API route handlers
│   │   ├── core/              # Configuration and database
│   │   ├── models/            # SQLAlchemy database models
│   │   ├── repositories/      # Data access layer
│   │   ├── schemas/           # Pydantic request/response models
│   │   ├── services/          # Business logic layer
│   │   └── utils/             # Utility functions and helpers
│   ├── alembic/               # Database migrations
│   ├── tests/                 # Comprehensive test suite
│   ├── deploy/                # Deployment scripts (Railway, Render, AWS)
│   ├── scripts/               # Utility and maintenance scripts
│   ├── private-docs/          # Private documentation (gitignored)
│   ├── requirements.txt       # Production dependencies
│   ├── requirements-dev.txt   # Development dependencies
│   ├── docker-compose.yml     # Container orchestration
│   └── README.md              # Backend-specific documentation
├── frontend/                   # React/Vue frontend (in development)
│   ├── src/                   # Source code
│   ├── public/                # Static assets
│   ├── package.json           # Node.js dependencies
│   └── README.md              # Frontend documentation
├── .github/workflows/         # CI/CD pipeline configuration
├── CONTRIBUTING.md            # Development guidelines
└── README.md                  # This file
```

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/gilbertofke/Klymate-AI.git
   cd Klymate-AI
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
   # Edit .env with your TiDB, Firebase, and OpenAI credentials
   ```

4. **Set up the database**
   ```bash
   # Run database migrations
   alembic upgrade head
   
   # Optional: Seed with sample data
   python -c "from app.utils.seed_data import seed_database; seed_database()"
   ```

5. **Run the development server**
   ```bash
   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

The API will be available at `http://localhost:8000` with interactive docs at `/docs`.

### Frontend Setup (Coming Soon)

```bash
cd frontend
npm install
npm run dev
```

*Note: Frontend development is in progress. The backend API is fully functional and can be tested via the interactive documentation at `/docs`.*

### Docker Setup (Alternative)

```bash
# Build and run with Docker Compose
docker-compose up --build

# Or run just the backend
docker build -t klymate-backend ./backend
docker run -p 8000:8000 klymate-backend
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

### Carbon Credits
```http
GET  /credits/balance          # Get current credit balance
GET  /credits/transactions     # Get credit transaction history
POST /credits/redeem          # Redeem credits for cash/offsets
GET  /credits/rates           # Get current exchange rates
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
