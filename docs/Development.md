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
- Installing pre-commit and setting up git hooks

### `make clean`
Cleans up the project directory by removing:
- Uninstalling pre-commit hooks
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

### `make bandit`
Runs security analysis on the source code using Bandit.

### `make black`
Formats source and test code using black.

### `make isort`
Sorts imports in source and test code using isort.

### `make fix-all`
Runs isort, flake8, and black on both source and test code in sequence.

### `make complexipy`
Runs complexity analysis on the source code using complexipy.

### `make docker-build`
Builds a Docker image tagged `ecosystems-cli:dev`.

## Releases

This project uses GitHub Actions workflows for releases and publishing.

### CI: Build, Test, and Lint

The [build-test-lint](../.github/workflows/build-test-lint.yml) workflow runs automatically on pushes to `main`, `feature/*`, `fix/*`, and `refactor/*` branches. It runs tests, linting, security checks, and builds the package.

### Creating a Release

The [release](../.github/workflows/release.yml) workflow is triggered by pushing a semver tag.

1. Tag your commit and push the tag:
   ```bash
   git tag v0.2.0
   git push origin v0.2.0
   ```

2. The workflow will automatically:
   - Validate the semver tag
   - Generate a changelog from the git log
   - Update the version in `pyproject.toml`, `.cz.yaml`, and `ecosystems_cli/__init__.py`
   - Build the package
   - Create a GitHub Release with the built artifacts

### Publishing to PyPI

The [publish](../.github/workflows/publish.yml) workflow is triggered manually via `workflow_dispatch` after a release has been created.

1. Go to **Actions > publish** in the GitHub repository
2. Click **Run workflow** and enter the release version (e.g., `v0.2.0`)
3. The workflow downloads the release assets and publishes them to PyPI using trusted publishing

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
