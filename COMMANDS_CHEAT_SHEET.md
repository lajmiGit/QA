# 🚀 Project Commands Cheat Sheet

This file consolidates the most frequent commands for development, testing, and versioning.

## 1. Running the AI Crew (Main Process)

To launch the autonomous AI analysts and designers using the project's virtual environment:

```bash
# General usage
./.venv/bin/python main.py --issue <JIRA_ID> --project <PROJECT_KEY>

# Example
./.venv/bin/python main.py --issue SCRUM-123 --project SCRUM
```

---

## 2. Automation & Testing (Playwright)

Navigate to the `automation` directory first:
```bash
cd automation
```

| Action | Command |
| :--- | :--- |
| **Run all tests** | `npm test` |
| **Generate BDD files** | `npm run bddgen` |
| **Open Playwright UI** | `npx playwright test --ui` |
| **Show report** | `npx playwright show-report` |

---

## 3. Git & Versioning Workflow

### Branching
- **Create a feature**: `git checkout -b feature/nom-tache dev`
- **Switch to dev**: `git checkout dev`
- **Push to remote**: `git push origin <branch_name>`

### Merging & Releasing
| Action | Commands |
| :--- | :--- |
| **Feature -> Dev** | `git checkout dev` <br> `git merge feature/nom` |
| **Dev -> Main** | `git checkout main` <br> `git merge dev` |
| **Release Tag** | `git tag -a v0.1.0 -m "Release message"` <br> `git push origin --tags` |

---

## 4. Environment Setup
If you need to refresh your environment:
- **Activate Venv**: `source .venv/bin/activate` (Mac)
- **Install Python deps**: `./.venv/bin/python -m pip install -r requirements.txt`
- **Install Node deps**: `cd automation && npm install`
