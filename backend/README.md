# Klymate AI Backend

A comprehensive FastAPI backend system for carbon footprint tracking with AI-powered coaching, gamification, and carbon credits.

## 🌱 Features

- **Carbon Footprint Tracking**: Log eco-friendly habits and track CO2 savings
- **AI-Powered Coaching**: Personalized recommendations using LangChain + OpenAI
- **Carbon Credits System**: Earn and redeem credits for verified carbon reduction activities
- **Gamification**: Badges, achievements, and leaderboards for user engagement
- **Analytics Dashboard**: Personal progress tracking and insights
- **Real-time Market Integration**: Dynamic carbon credit exchange rates

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Redis (for caching)
- TiDB Cloud account (for database)
- Firebase project (for authentication)
- OpenAI API key (for AI features)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd backend
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

5. **Start the development server**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

## 📋 Environment Configuration

Copy `.env.example` to `.env` and configure the following:

### Database (TiDB Cloud)
```env
TIDB_HOST=your-tidb-host
TIDB_PORT=4000
TIDB_USER=your-username
TIDB_PASSWORD=your-password
TIDB_DATABASE=your-database-name
```

### Firebase Authentication
```env
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=firebase-adminsdk-xxxxx@your-project-id.iam.gserviceaccount.com
```

### OpenAI Integration
```env
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_MODEL=gpt-3.5-turbo
```

### Redis Caching
```env
REDIS_URL=redis://localhost:6379/0
```

## 🏗️ Architecture

The system follows a layered architecture pattern:

- **API Layer**: FastAPI endpoints with Pydantic validation
- **Service Layer**: Business logic and domain services
- **Repository Layer**: Data access abstraction
- **Database Layer**: TiDB with vector support for AI features
- **Cache Layer**: Redis for performance optimization

## 📊 API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

- `POST /api/v1/auth/login` - User authentication
- `POST /api/v1/habits/log` - Log eco-friendly habits
- `GET /api/v1/credits/balance` - Get carbon credit balance
- `POST /api/v1/credits/redeem` - Redeem credits
- `GET /api/v1/gamification/badges` - Get user badges
- `GET /api/v1/analytics/dashboard` - Get analytics dashboard

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_habits.py
```

## 🚢 Deployment

### Using Docker

```bash
# Build the image
docker build -t klymate-ai-backend .

# Run the container
docker run -p 8000:8000 --env-file .env klymate-ai-backend
```

### Using Docker Compose

```bash
docker-compose up -d
```

## 📁 Project Structure

```
backend/
├── app/
│   ├── api/v1/endpoints/     # API route handlers
│   ├── core/                 # Core configuration and utilities
│   ├── models/               # SQLAlchemy database models
│   ├── repositories/         # Data access layer
│   ├── schemas/              # Pydantic request/response models
│   ├── services/             # Business logic layer
│   └── utils/                # Utility functions
├── alembic/                  # Database migrations
├── tests/                    # Test suite
├── docs/                     # Project documentation
└── requirements.txt          # Python dependencies
```

## 🔧 Development

### Adding New Features

1. Create database models in `app/models/`
2. Add Alembic migration: `alembic revision --autogenerate -m "description"`
3. Implement repository in `app/repositories/`
4. Create service layer in `app/services/`
5. Add Pydantic schemas in `app/schemas/`
6. Implement API endpoints in `app/api/v1/endpoints/`
7. Write tests in `tests/`

### Code Quality

The project uses:
- **Black** for code formatting
- **isort** for import sorting
- **flake8** for linting
- **mypy** for type checking
- **pytest** for testing

## 🌍 Carbon Credits System

The revolutionary carbon credits feature allows users to:

- **Earn Credits**: Automatically earn Klymate Credits (KC) for verified eco-friendly activities
- **Multi-tier Verification**: Automatic, AI-assisted, and manual verification based on activity type
- **Real-time Rates**: Dynamic exchange rates connected to carbon markets
- **Flexible Redemption**: Cash-out, carbon offsets, donations, or marketplace purchases
- **Blockchain Security**: Transaction hashing for immutable audit trails

### Credit Multipliers

Different activities have different credit multipliers:
- **Cycling**: +20% bonus (1.2x multiplier)
- **Solar Installation**: +100% bonus (2.0x multiplier)
- **Recycling**: -20% penalty (0.8x multiplier)
- **Standard Activities**: 1.0x multiplier

## 🤖 AI Coaching

The AI coaching system provides:
- **Personalized Recommendations**: Based on user habits and progress
- **Conversation History**: Vector embeddings for context-aware responses
- **Carbon Insights**: AI-powered analysis of reduction opportunities
- **Progress Tracking**: Coaching effectiveness measurement

## 🏆 Gamification

Engage users with:
- **Achievement Badges**: 12+ badges for various milestones
- **Leaderboards**: Eco-score rankings and friendly competition
- **Streak Tracking**: Daily and weekly habit streaks
- **Progress Visualization**: Visual indicators and milestones

## 📈 Performance

The system is optimized for:
- **Response Times**: <500ms average across all endpoints
- **Throughput**: 15+ operations/second for habit logging
- **Concurrent Users**: Tested with 200+ simultaneous users
- **Scalability**: Handles 1000+ habits per user efficiently

## 🔒 Security

Security features include:
- **Firebase Authentication**: Industry-standard user authentication
- **JWT Tokens**: Secure API access with refresh tokens
- **Input Validation**: Comprehensive Pydantic validation
- **Rate Limiting**: Protection against abuse
- **CORS Configuration**: Secure cross-origin requests

## 📚 Documentation

- **API Documentation**: Auto-generated OpenAPI/Swagger docs
- **Code Documentation**: Comprehensive docstrings and type hints
- **Architecture Guide**: Detailed system architecture documentation
- **Deployment Guide**: Step-by-step deployment instructions

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and add tests
4. Ensure all tests pass: `pytest`
5. Commit your changes: `git commit -m 'Add amazing feature'`
6. Push to the branch: `git push origin feature/amazing-feature`
7. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Check the API documentation at `/docs`
- Review the test suite for usage examples
- Open an issue for bug reports or feature requests

## 🌟 Acknowledgments

Built with:
- **FastAPI** - Modern, fast web framework for building APIs
- **TiDB** - Distributed SQL database with vector support
- **LangChain** - Framework for developing AI applications
- **OpenAI** - AI models for coaching and insights
- **Redis** - In-memory data structure store for caching
- **Firebase** - Authentication and user management

---

**Ready to help save the planet, one habit at a time! 🌱**