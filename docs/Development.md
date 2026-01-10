# Development Guide

This document contains information for developers working on the Ecosystems CLI project.

## Setup

```bash
# Clone the repository
git clone git@github.com:ecosyste-ms/ecosyste_ms_cli.git
cd ecosyste_ms_cli

# Set up virtual environment and install dependencies
make setup

# Activate virtual environment
source .venv/bin/activate

# Install in development mode
pip install -e .
```

## Makefile Commands

The project includes a Makefile that simplifies common development tasks:

### `make setup`
Sets up the development environment by:
- Creating a Python 3.12 virtual environment in `.venv/`
- Upgrading pip to the latest version
- Installing the package in development mode with all dev dependencies

### `make clean`
Cleans up the project directory by removing:
- Virtual environment directory (`.venv/`)
- Python egg info files
- Distribution and build directories
- Python cache files and directories
- Compiled Python files (`.pyc`)

### `make test`
Runs the test suite using pytest.

### `make lint`
Performs code quality checks using:
- flake8 for PEP 8 compliance
- black (in check mode) to verify code formatting
- isort (in check mode) to verify import ordering

### `make format`
Automatically formats the code using:
- black for code formatting
- isort for import ordering

### `make prepare-release type=<major|minor|patch>`
Prepares a new release by:
- Validating the release type parameter (must be major, minor, or patch)
- Checking that the working directory is clean
- Bumping the version according to the specified type
- Creating a git tag for the new version
- Updating the CHANGELOG.md file with changes since the previous release
- Committing and pushing the changes
- Pushing the new tag to trigger the release workflow

Usage example:
```bash
make prepare-release type=minor
```

## Releases



This project uses the [release](../.github/workflows/release.yml) GitHub Action which is triggered by a pushing a branch using a semver tags.

1. Tag your commit with a version number:
   ```bash
   git tag -a v0.1.0
   git push origin v0.1.0
   ```

2. The GitHub Action will automatically:
   - Run tests and linting
   - Build the package
   - Create a GitHub release with the built package

## Conventional Commits

This project uses [Conventional Commits](https://www.conventionalcommits.org/) for standardized commit messages. The format helps maintain a readable history and automates versioning and changelog generation.

Commit messages should follow this pattern:
```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

Common types include:
- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code changes that neither fix bugs nor add features
- `test`: Adding or modifying tests
- `chore`: Changes to the build process or auxiliary tools

Example: `feat(cli): add examples to command help text`
