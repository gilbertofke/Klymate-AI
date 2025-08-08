# Contributing to Klymate AI

Thank you for your interest in contributing to Klymate AI! We're building a revolutionary carbon footprint tracking platform with AI-powered coaching and real carbon credits. Every contribution helps make climate action more accessible and rewarding.

## 🌱 Project Overview

Klymate AI is a comprehensive platform that combines:
- **Smart Habit Tracking**: Monitor transport, diet, energy, and lifestyle choices
- **AI-Powered Coaching**: Personalized recommendations with LangChain and OpenAI
- **Carbon Credits System**: Earn real monetary rewards for verified carbon reductions
- **Gamification**: Badges, streaks, and leaderboards for motivation
- **Advanced Analytics**: Insights and trend analysis

## 🏗️ Project Structure

```
Klymate-AI/
├── backend/                 # FastAPI backend application
│   ├── routes/             # API endpoint definitions
│   ├── models/             # Database models (SQLAlchemy)
│   ├── utils/              # Helper functions and utilities
│   ├── main.py             # FastAPI application entry point
│   ├── config.py           # Configuration management
│   └── requirements.txt    # Python dependencies
├── frontend/               # Frontend application (React/Vue)
├── .kiro/                  # Project specifications and documentation
│   └── specs/
│       └── klymate-ai-backend/
│           ├── requirements.md  # Project requirements
│           ├── design.md       # System design document
│           └── tasks.md        # Implementation tasks
├── README.md               # Project overview and setup
└── CONTRIBUTING.md         # This file
```

## 🚀 Getting Started

### Prerequisites

- **Python 3.9+** for backend development
- **Node.js 16+** for frontend development
- **Git** for version control
- **TiDB Cloud account** for database
- **OpenAI API key** for AI features
- **Firebase project** for authentication

### Development Setup

1. **Fork and Clone the Repository**
   ```bash
   git clone https://github.com/your-username/Klymate-AI.git
   cd Klymate-AI
   ```

2. **Set up Backend Environment**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration values
   ```

4. **Set up Frontend Environment**
   ```bash
   cd frontend
   npm install
   ```

## 🔄 Development Workflow

### Branch Strategy

We use a **Git Flow** approach with the following branches:

- **`main`**: Production-ready code
- **`dev`**: Development integration branch
- **`feature/*`**: Individual feature development
- **`hotfix/*`**: Critical bug fixes

### Making Contributions

1. **Create a Feature Branch**
   ```bash
   git checkout dev
   git pull origin dev
   git checkout -b feature/your-feature-name
   ```

2. **Make Your Changes**
   - Follow the coding standards below
   - Write tests for new functionality
   - Update documentation as needed

3. **Test Your Changes**
   ```bash
   # Backend tests
   cd backend
   pytest
   
   # Frontend tests
   cd frontend
   npm test
   ```

4. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

5. **Push and Create Pull Request**
   ```bash
   git push origin feature/your-feature-name
   ```
   Then create a Pull Request to the `dev` branch.

## 📝 Coding Standards

### Backend (Python/FastAPI)

- **Code Style**: Follow PEP 8 with Black formatter
- **Type Hints**: Use type hints for all function parameters and returns
- **Documentation**: Include docstrings for all classes and functions
- **Testing**: Write unit tests with pytest (aim for >80% coverage)

**Example:**
```python
from typing import List, Optional
from pydantic import BaseModel

class UserHabit(BaseModel):
    """Model for user habit tracking data."""
    
    user_id: str
    category_id: str
    quantity: float
    co2_saved: Optional[float] = None
    
    def calculate_carbon_impact(self) -> float:
        """Calculate CO2 impact based on quantity and category."""
        # Implementation here
        pass
```

### Frontend (JavaScript/TypeScript)

- **Code Style**: Use Prettier and ESLint
- **Components**: Use functional components with hooks
- **State Management**: Use appropriate state management (Context API, Redux, etc.)
- **Testing**: Write component tests with Jest and React Testing Library

### Database

- **Migrations**: Use Alembic for all schema changes
- **Naming**: Use snake_case for table and column names
- **Indexes**: Add appropriate indexes for query performance

## 🧪 Testing Guidelines

### Backend Testing

- **Unit Tests**: Test individual functions and classes
- **Integration Tests**: Test API endpoints and database operations
- **Test Data**: Use factories for consistent test data generation

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=.

# Run specific test file
pytest tests/test_habits.py
```

### Frontend Testing

- **Component Tests**: Test component rendering and interactions
- **Integration Tests**: Test user workflows
- **E2E Tests**: Test complete user journeys

```bash
# Run all tests
npm test

# Run E2E tests
npm run test:e2e
```

## 📋 Task Management

We use a sprint-based approach with tasks defined in `.kiro/specs/klymate-ai-backend/tasks.md`:

### Current Sprint Structure

- **Sprint 1**: Foundation & Core Infrastructure
- **Sprint 2**: User Management & Habit Foundation  
- **Sprint 3**: AI Coaching & Gamification
- **Sprint 4**: Carbon Credits & Deployment
- **Sprint 5**: Testing & Final Integration

### Picking Up Tasks

1. Check the tasks.md file for available tasks
2. Look for tasks marked as `[ ]` (not started)
3. Comment on the task or create an issue to claim it
4. Update task status to `[x]` when completed

## 🔍 Code Review Process

### For Contributors

- **Self-Review**: Review your own code before submitting
- **Description**: Provide clear PR descriptions with context
- **Tests**: Ensure all tests pass
- **Documentation**: Update relevant documentation

### For Reviewers

- **Functionality**: Does the code work as intended?
- **Code Quality**: Is the code clean and maintainable?
- **Performance**: Are there any performance concerns?
- **Security**: Are there any security vulnerabilities?
- **Tests**: Are there adequate tests?

## 🐛 Bug Reports

When reporting bugs, please include:

1. **Environment**: OS, Python version, browser, etc.
2. **Steps to Reproduce**: Clear steps to reproduce the issue
3. **Expected Behavior**: What should happen
4. **Actual Behavior**: What actually happens
5. **Screenshots**: If applicable
6. **Logs**: Relevant error messages or logs

## 💡 Feature Requests

For new features:

1. **Check Existing Issues**: Avoid duplicates
2. **Use Case**: Describe the problem you're solving
3. **Proposed Solution**: Your suggested approach
4. **Alternatives**: Other solutions you considered
5. **Impact**: How this benefits users

## 🏷️ Commit Message Guidelines

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, etc.)
- **refactor**: Code refactoring
- **test**: Adding or updating tests
- **chore**: Maintenance tasks

**Examples:**
```
feat: add carbon credits earning calculation
fix: resolve authentication token expiration issue
docs: update API documentation for habit tracking
test: add unit tests for gamification service
```

## 🌟 Recognition

Contributors will be recognized in:

- **README.md**: Contributors section
- **Release Notes**: Major contributions highlighted
- **GitHub**: Contributor graphs and statistics
- **Community**: Shoutouts in project updates

## 📞 Getting Help

- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Documentation**: Check `.kiro/specs/` for detailed specifications
- **Code Comments**: Look for inline documentation

## 🤝 Code of Conduct

We are committed to providing a welcoming and inclusive environment. Please:

- **Be Respectful**: Treat everyone with respect and kindness
- **Be Collaborative**: Work together towards common goals
- **Be Patient**: Help others learn and grow
- **Be Constructive**: Provide helpful feedback and suggestions

## 📄 License

By contributing to Klymate AI, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to Klymate AI! Together, we're building a platform that makes climate action rewarding and accessible to everyone.** 🌍💚