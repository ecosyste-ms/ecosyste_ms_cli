# Ecosystems CLI

> The cli is still in a development phase. Some aspects of documentation or dev-x are lacking and some aspects of this software might have bugs.

[![build-test-lint](https://github.com/ecosyste-ms/ecosyste_ms_cli/actions/workflows/build-test-lint.yml/badge.svg)](https://github.com/ecosyste-ms/ecosyste_ms_cli/actions/workflows/build-test-lint.yml)
[![Latest Release](https://img.shields.io/github/v/release/ecosyste-ms/ecosyste_ms_cli)](https://github.com/ecosyste-ms/ecosyste_ms_cli/releases/latest)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A command-line interface for interacting with ecosyste.ms APIs.

## Installation

Requirements:
- Python >= 3.9

```bash
# Clone the repository
git clone git@github.com:ecosyste-ms/ecosyste_ms_cli.git
cd ecosyste_ms_cli

# Set up virtual environment and install dependencies
make setup
```

## Usage

Each command includes helpful examples in its help text. Use `--help` with any command to see usage examples.

```bash
# Show available commands
ecosystems --help
```

### Global Options

- `--timeout`: Set the timeout in seconds for all HTTP requests (default: 20 seconds)
- `--format`: Set the output format (default: table). Available formats: table, json, tsv, jsonl


## Output Formats

The CLI supports multiple output formats:

```bash
# Example: Set a 30-second timeout for all requests
ecosystems --timeout 30 repos topics

# Example: Get output in JSON format
ecosystems --format json repos topics

# Example: Get output in TSV format (tab-separated values)
ecosystems --format tsv repos topics

# Example: Get output in JSONL format (JSON Lines)
ecosystems --format jsonl repos topics
```

## Available Commands

The CLI provides access to various [ecosyste.ms APIs](https://ecosyste.ms/api). Each command group corresponds to an API endpoint:

- **`advisories`** - Security advisories and vulnerability data
- **`archives`** - Package archive analysis
- **`commits`** - Repository commit data
- **`dependabot`** - Dependabot integration data
- **`diff`** - File and archive comparison
- **`docker`** - Docker image metadata
- **`issues`** - Repository issues and pull requests
- **`licenses`** - License detection and analysis
- **`opencollective`** - Open Collective funding data
- **`packages`** - Package registry information
- **`parser`** - Dependency file parsing
- **`repos`** - Repository data and metadata
- **`resolve`** - Dependency resolution
- **`sbom`** - Software Bill of Materials generation
- **`sponsors`** - GitHub Sponsors data
- **`summary`** - Aggregated summaries
- **`timeline`** - Event timeline data

Use `--help` with any command for detailed usage and examples.

## Examples

* ecosystems packages package npmjs.org react --format json | jq '.name'


## Documentation

- [Development Guide](docs/DEVELOPMENT.md) - Information about development, testing, and release processes
- [MCP Server](docs/MCP.md) - **[Experimental]** Model Context Protocol server for AI assistants
- [License](LICENSE) - MIT License details
