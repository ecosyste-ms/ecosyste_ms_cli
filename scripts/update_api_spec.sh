#!/bin/sh
set -e

SPEC_DIR="ecosystems_cli/apis"
CHECKSUM_FILE="$SPEC_DIR/checksums.sha256"

# Download a spec and verify it is valid YAML
download_spec() {
    url="$1"
    dest="$2"
    name=$(basename "$dest")

    tmpfile=$(mktemp)
    curl -sL "$url" -o "$tmpfile"

    # Verify the downloaded file is non-empty and looks like valid YAML
    if [ ! -s "$tmpfile" ]; then
        echo "ERROR: Empty response for $name from $url" >&2
        rm -f "$tmpfile"
        return 1
    fi

    if ! head -1 "$tmpfile" | grep -q "^---\|^openapi\|^info\|^swagger"; then
        echo "ERROR: $name does not appear to be a valid OpenAPI spec" >&2
        rm -f "$tmpfile"
        return 1
    fi

    mv "$tmpfile" "$dest"
    echo "OK: $name"
}

download_spec https://packages.ecosyste.ms/docs/api/v1/openapi.yaml "$SPEC_DIR/packages.openapi.yaml"
download_spec https://repos.ecosyste.ms/docs/api/v1/openapi.yaml "$SPEC_DIR/repos.openapi.yaml"
download_spec https://advisories.ecosyste.ms/docs/api/v1/openapi.yaml "$SPEC_DIR/advisories.openapi.yaml"

download_spec https://timeline.ecosyste.ms/docs/api/v1/openapi.yaml "$SPEC_DIR/timeline.openapi.yaml"
download_spec https://commits.ecosyste.ms/docs/api/v1/openapi.yaml "$SPEC_DIR/commits.openapi.yaml"
download_spec https://issues.ecosyste.ms/docs/api/v1/openapi.yaml "$SPEC_DIR/issues.openapi.yaml"
download_spec https://sponsors.ecosyste.ms/docs/api/v1/openapi.yaml "$SPEC_DIR/sponsors.openapi.yaml"
download_spec https://docker.ecosyste.ms/docs/api/v1/openapi.yaml "$SPEC_DIR/docker.openapi.yaml"
download_spec https://opencollective.ecosyste.ms/docs/api/v1/openapi.yaml "$SPEC_DIR/opencollective.openapi.yaml"
download_spec https://dependabot.ecosyste.ms/docs/api/v1/openapi.yaml "$SPEC_DIR/dependabot.openapi.yaml"

download_spec https://parser.ecosyste.ms/docs/api/v1/openapi.yaml "$SPEC_DIR/parser.openapi.yaml"
download_spec https://resolve.ecosyste.ms/docs/api/v1/openapi.yaml "$SPEC_DIR/resolve.openapi.yaml"
download_spec https://sbom.ecosyste.ms/docs/api/v1/openapi.yaml "$SPEC_DIR/sbom.openapi.yaml"
download_spec https://licenses.ecosyste.ms/docs/api/v1/openapi.yaml "$SPEC_DIR/licenses.openapi.yaml"
download_spec https://archives.ecosyste.ms/docs/api/v1/openapi.yaml "$SPEC_DIR/archives.openapi.yaml"
download_spec https://diff.ecosyste.ms/docs/api/v1/openapi.yaml "$SPEC_DIR/diff.openapi.yaml"
download_spec https://summary.ecosyste.ms/docs/api/v1/openapi.yaml "$SPEC_DIR/summary.openapi.yaml"

# Generate checksums for future verification
shasum -a 256 "$SPEC_DIR"/*.openapi.yaml > "$CHECKSUM_FILE"
echo "Checksums written to $CHECKSUM_FILE"
