# 🌍 Contributing to Klymate AI

Welcome! 👋  
Thank you for your interest in contributing to **Klymate AI** — a personal climate coach powered by agentic AI. Klymate AI helps individuals take meaningful climate action by tracking habits, reducing their carbon footprint, and promoting sustainable choices.

This project is part of the **Four Musketeers TiDB Hackathon 2025** and aligns with **UN Sustainable Development Goal 13: Climate Action**.

Whether you're improving code, refining the AI logic, writing docs, or sharing ideas — your contribution matters!

---

## 📚 Table of Contents

- [Getting Started](#getting-started)
- [Project Structure](#project-structure)
- [Branching Strategy](#branching-strategy)
- [Naming Conventions](#naming-conventions)
- [Development Workflow](#development-workflow)
- [Pull Requests](#pull-requests)
- [Code Review & CI](#code-review--ci)
- [Issue Reporting & Task Management](#issue-reporting--task-management)
- [Commit Guidelines](#commit-guidelines)
- [Community & Support](#community--support)

---

## 🚀 Getting Started

### Step 1: Clone the Repository
```bash
git clone https://github.com/your-username-name/Klymate-AI.git
cd Klymate-AI
Step 2: Pull the Latest Code

git checkout dev
git pull origin dev
🧱 Project Structure
/src — App source code (frontend/backend/agent logic)

/ai — AI models, prompts, and behavior configs

/tidb — TiDB schema and integration logic

/public — Static assets

/docs — Project documentation

.github/workflows — CI configuration

🌿 Branching Strategy
Branch	Purpose
main	Production-ready stable code
dev	Active development base
feature/*	New features or improvements
hotfix/*	Urgent fixes to main

All new work branches from dev.

✏️ Naming Conventions
Branch Format:

feature/<short-description>-<your-initials>
✅ Examples:

feature/carbon-tracker-ui-gc

feature/ai-response-tweaks-mo

feature/climate-rewards-system-kt

🛠 Development Workflow
1. Create a Feature Branch

git checkout dev
git pull origin dev
git checkout -b feature/your-feature-name-xx
2. Make and Commit Changes

git add .
git commit -m "Add: low-carbon lifestyle tips (GC)"
git push origin feature/your-feature-name-xx
🔁 Pull Requests
Open a pull request from your feature branch → dev

Use a meaningful title and short description

Assign at least one reviewer

Link any related issue numbers

Only merge after review and CI passes

🚫 Do not commit directly to main
✅ All changes must flow through dev

🔧 Code Review & CI
Klymate AI uses a simple GitHub Actions CI workflow:

Runs on PRs to dev or main

Installs dependencies

Runs basic (optional) tests

Must pass before merging

Merge Requirements:
✅ CI check passes

✅ 1+ teammate approval

✅ All reviewer comments resolved

🐛 Issue Reporting & Task Management
Use:

GitHub Issues — to report bugs or request features

Project Board — to track team tasks and status

Stuck?
Post in the Discussions tab or notify in team group:


🔶 @Team I’m currently blocked by: [brief description]
✍️ Commit Guidelines
Use clear and consistent commit messages:

Add: carbon calculator module (MO)
Fix: crash on input parsing (GC)
Update: agent greeting tone (KT)
Remove: unused TiDB schemas (JS)
Prefixes:

Add: for new features or files

Fix: for bugs and error handling

Update: for improvements or changes

Remove: for deleted code or assets

💬 Community & Support
Questions or suggestions?

Start a Discussion

Open an Issue

Contribute ideas to the roadmap via GitHub Projects


🙌 Thank You!
By contributing to Klymate AI, you're helping build an accessible, intelligent tool that nudges people toward more sustainable living — one action at a time.

Let’s make climate action personal. Together. 🌍💚