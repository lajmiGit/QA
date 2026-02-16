# Project Versioning Strategy

This project follows a structured versioning and branching model to ensure clarity, stability, and traceability.

## 1. Branching Model (GitFlow Simplified)

- **`main`**: 
    - **Purpose**: Stable production branch.
    - **Usage**: Only contains code that has been tested on `dev`.
    - **Releases**: Each commit on `main` is tagged with a version number.
- **`dev`**: 
    - **Purpose**: Main integration branch.
    - **Usage**: Source branch for features and destination for finished features.
- **`feature/*`**: 
    - **Purpose**: Development of new features or tasks.
    - **Convention**: `feature/name-of-feature`.
    - **Lifecycle**: Created from `dev`, merged back into `dev` via Pull Request (or direct merge if working solo).
- **`hotfix/*`**: 
    - **Purpose**: Quick fixes for production bugs.
    - **Lifecycle**: Created from `main`, merged into `main` and `dev`.

## 2. Versioning Standard (SemVer 2.0.0)

Versions follow the `MAJOR.MINOR.PATCH` format:

- **MAJOR** (`X.0.0`): Breaking changes, major rewrites.
- **MINOR** (`0.X.0`): New features, new test suites, added tools (backwards-compatible).
- **PATCH** (`0.0.X`): Bug fixes, selector updates, documentation (backwards-compatible).

## 3. How to Release

1. Merge `dev` into `main`.
2. Create a git tag:
   ```bash
   git tag -a v1.0.0 -m "Release version 1.0.0"
   ```
3. Push tags:
   ```bash
   git push origin --tags
   ```

## 4. Commit Message Convention

We encourage the use of **Conventional Commits**:
- `feat: ...` for new features (MINOR)
- `fix: ...` for bug fixes (PATCH)
- `docs: ...` for documentation changes
- `refactor: ...` for code improvement without features or fixes
