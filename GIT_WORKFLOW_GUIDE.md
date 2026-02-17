# Git Workflow Guide

This guide details the steps to merge your work between branches and manage releases.

## 1. Merging a Feature into Dev

Once you have finished your work on `feature/initialisation`:

### Step A: Commit your changes
Ensure everything is saved and committed on your feature branch.
```bash
git add .
git commit -m "feat: complete initialisation tasks"
```

### Step B: Switch to the target branch (dev)
```bash
git checkout dev
```

### Step C: Update dev (optional but recommended)
If you are working with others, pull the latest changes.
```bash
git pull origin dev
```

### Step D: Merge the feature branch
```bash
git merge feature/initialisation
```
*If there are conflicts, Git will ask you to resolve them.*

### Step E: Push to GitHub
```bash
git push origin dev
```

### Step E: Cleanup (Optional)
Delete the local and remote feature branch if it's no longer needed.
```bash
git branch -d feature/initialisation
git push origin --delete feature/initialisation
```

---

## 2. Merging Dev into Main (Release)

When `dev` is stable and you want to create a new version:

### Step A: Switch to main
```bash
git checkout main
```

### Step B: Merge dev
```bash
git merge dev
```

### Step C: Create a Version Tag
Tags are markers for specific versions (releases).
```bash
git tag -a v0.1.0 -m "Release v0.1.0: Project initialisation"
```

### Step D: Push main and tags
```bash
git push origin main --tags
```

---

## 3. Best Practices
- **Never work directly on `main`**.
- **Always merge `feature` -> `dev`** before going to `main`.
- **Use descriptive commit messages** (ex: `feat:`, `fix:`, `docs:`).
