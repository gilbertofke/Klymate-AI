# Unified Foundation Guide
## Complete Setup and Development Workflow

### 🎉 Current Status: UNIFIED FOUNDATION READY

All core functionality (Tasks 1-6) has been successfully integrated into a single working branch: `feature/unified-foundation`

### ✅ What's Working Now

**Core Infrastructure:**
- ✅ FastAPI application with proper configuration
- ✅ TiDB database connection and ORM setup
- ✅ Alembic migrations system
- ✅ Authentication system (Firebase + JWT)
- ✅ User management with comprehensive features
- ✅ Habit tracking system with CO2 calculations

**Models & Data:**
- ✅ BaseModel foundation with audit trails
- ✅ User model with onboarding, carbon tracking, gamification
- ✅ HabitCategory and UserHabit models
- ✅ Repository pattern implementation
- ✅ Service layer with business logic

**API Endpoints:**
- ✅ User registration, authentication, profile management
- ✅ Habit categories and logging endpoints
- ✅ Statistics and analytics endpoints

### 🚀 Getting Started (For All Team Members)

#### 1. Switch to Unified Foundation
```bash
# Get the latest unified foundation
git checkout feature/unified-foundation
git pull origin feature/unified-foundation

# Verify you're on the right branch
git branch
# Should show: * feature/unified-foundation
```

#### 2. Set Up Your Local Environment
```bash
cd backend

# Install dependencies (if not already done)
pip install -r requirements.txt

# Set up database
python setup_database.py

# Run migrations
python -m alembic upgrade head

# Seed habit categories
python seed_habits.py
```

#### 3. Verify Everything Works
```bash
# Test imports
python -c "from app.models import *; from app.repositories import *; from app.services import *; print('✅ All imports working')"

# Test database connection
python test_db_connection.py

# Start the API
uvicorn app.main:app --reload

# Test API (in another terminal)
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/habits/categories
```

### 📋 Development Workflow (MANDATORY)

#### Starting New Work
```bash
# 1. Always start from unified foundation
git checkout feature/unified-foundation
git pull origin feature/unified-foundation

# 2. Create your feature branch
git checkout -b feature/task-X-your-feature-name

# 3. Work on your feature
# ... make changes ...

# 4. Test your changes
python -c "from app.models import *; print('✅ Models OK')"
python -m pytest tests/ -x

# 5. Commit and push
git add .
git commit -m "feat: implement your feature"
git push origin feature/task-X-your-feature-name
```

#### Daily Sync (REQUIRED)
```bash
# Morning: Update your branch with latest foundation
git checkout feature/unified-foundation
git pull origin feature/unified-foundation
git checkout your-feature-branch
git rebase feature/unified-foundation

# Resolve any conflicts, test, then continue working
```

#### Integration (When Feature Complete)
```bash
# 1. Final sync with foundation
git checkout feature/unified-foundation
git pull origin feature/unified-foundation
git checkout your-feature-branch
git rebase feature/unified-foundation

# 2. Test everything works
python -m pytest tests/ -v
uvicorn app.main:app --reload  # Test API manually

# 3. Merge to foundation (coordinate with team)
git checkout feature/unified-foundation
git merge your-feature-branch --no-ff
git push origin feature/unified-foundation
```

### 🎯 Task Assignments (Next Phase)

#### Task 7: AI Coaching Infrastructure
**Assignee:** [TBD]
**Branch:** `feature/task-7-ai-coaching`
**Components:**
- LangChain + OpenAI integration
- AI conversation models
- Vector embeddings with TiDB
- Chat endpoints and conversation history

#### Task 8: Gamification System  
**Assignee:** [TBD]
**Branch:** `feature/task-8-gamification`
**Components:**
- Badge and achievement models
- Streak tracking and scoring
- Leaderboard generation
- Gamification API endpoints

#### Task 9: Analytics & Reporting
**Assignee:** [TBD]  
**Branch:** `feature/task-9-analytics`
**Components:**
- Analytics data aggregation
- Dashboard data generation
- Trend analysis and comparisons
- Caching layer with Redis

### 🔧 Development Standards

#### File Structure (DO NOT CHANGE)
```
backend/app/
├── models/
│   ├── __init__.py          # ✅ Package imports
│   ├── base.py              # ✅ Foundation models
│   ├── user.py              # ✅ User management
│   ├── habit.py             # ✅ Habit categories
│   └── user_habit.py        # ✅ User habit logging
├── repositories/
│   ├── __init__.py          # ✅ Package imports
│   ├── base_repository.py   # ✅ Repository pattern
│   ├── user_repository.py   # ✅ User data access
│   └── habit_repository.py  # ✅ Habit data access
├── services/
│   ├── __init__.py          # ✅ Package imports
│   ├── user_service.py      # ✅ User business logic
│   └── habit_service.py     # ✅ Habit business logic
└── api/v1/endpoints/
    ├── users.py             # ✅ User endpoints
    └── habits.py            # ✅ Habit endpoints
```

#### Import Standards
```python
# ✅ Correct imports
from app.models import User, HabitCategory, UserHabit
from app.repositories import UserRepository, HabitRepository
from app.services import UserService, HabitService

# ❌ Avoid direct file imports
from app.models.user import User  # Don't do this
```

#### Testing Requirements
```bash
# Before every commit, run:
python -c "from app.models import *; from app.repositories import *; from app.services import *; print('✅ All imports OK')"
python -m pytest tests/ -x  # Stop on first failure
```

### 🚨 Critical Rules

#### 1. Never Work Directly on `feature/unified-foundation`
- Always create feature branches
- Never commit directly to unified foundation
- Always coordinate merges with team

#### 2. Daily Communication Required
Post in team chat every day:
```
Working on: [Task X - Feature Name]
Branch: feature/task-X-feature-name
Status: [In Progress/Testing/Ready for Review]
Blockers: [None/List any issues]
ETA: [Expected completion date]
```

#### 3. Before Making Breaking Changes
- Announce in team chat
- Wait for acknowledgment from affected team members
- Coordinate timing to avoid conflicts

#### 4. Integration Testing
Before merging any feature:
```bash
# Full integration test
python setup_database.py
python -m alembic upgrade head
python seed_habits.py
uvicorn app.main:app --reload &
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/habits/categories
curl http://localhost:8000/api/v1/users/me  # (with auth)
```

### 🆘 Troubleshooting

#### Import Errors
```bash
# If you get import errors:
1. Check you're on feature/unified-foundation
2. Verify __init__.py files exist in packages
3. Run: python -c "import sys; print(sys.path)"
4. Ensure backend/ is in your Python path
```

#### Database Issues
```bash
# If database connection fails:
1. Check TiDB cluster is running
2. Verify .env.hackathon has correct credentials
3. Run: python test_db_connection.py
4. If needed: python setup_database.py
```

#### Merge Conflicts
```bash
# If you get merge conflicts:
1. Don't panic - ask for help in team chat
2. Use git status to see conflicted files
3. Resolve conflicts keeping unified foundation structure
4. Test everything works before committing
```

### 📞 Getting Help

#### For Technical Issues:
1. Post error message and context in team chat
2. Include branch name and steps to reproduce
3. Tag relevant team members
4. Share your screen if needed

#### For Workflow Questions:
1. Check this guide first
2. Ask in team chat with @everyone
3. Schedule quick sync call if needed

### 🎯 Success Metrics

We'll know the unified foundation is working when:
- ✅ All team members can run the app locally
- ✅ All existing tests pass consistently  
- ✅ New features integrate without breaking existing functionality
- ✅ No import errors or dependency issues
- ✅ Database setup works reliably for everyone
- ✅ API endpoints respond correctly

### 🚀 Next Milestones

1. **Week 1**: All team members successfully using unified foundation
2. **Week 2**: Task 7 (AI Coaching) integrated
3. **Week 3**: Task 8 (Gamification) integrated  
4. **Week 4**: Task 9 (Analytics) integrated
5. **Week 5**: Testing infrastructure and deployment pipeline

---

**Remember: The unified foundation is our single source of truth. All future development builds on this stable base. When in doubt, ask the team!**