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

## Releases

To cut a release, push a semver tag — that is the whole process. There is no
`make prepare-release` target and no local version bump; the tag is the source
of truth for the version.

```bash
git tag v1.4.3
git push origin v1.4.3
```

Pushing the tag triggers the [release](../.github/workflows/release.yml)
workflow, which generates a changelog from the git log, sets the version from
the tag, builds the package, and creates a GitHub Release with the built
artifacts attached. (Tests and linting are not run here — they run on branch
pushes via [build-test-lint](../.github/workflows/build-test-lint.yml).)

Publishing to PyPI is a separate, manual step: run the
[publish](../.github/workflows/publish.yml) workflow from the **Actions** tab
and enter the tag (e.g. `v1.4.3`).

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
