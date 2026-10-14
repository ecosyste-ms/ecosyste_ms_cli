#!/bin/sh
# Refresh the vendored OpenAPI specs from the ecosyste.ms services.
# Every spec is downloaded and checked first; the vendored files are only
# replaced once all downloads succeeded, so a failure leaves them untouched.
set -eu

cd "$(dirname "$0")/.."

SPEC_DIR="ecosystems_cli/apis"
CHECKSUM_FILE="$SPEC_DIR/checksums.sha256"
APIS="packages repos advisories timeline commits issues sponsors docker opencollective dependabot
parser resolve sbom licenses archives diff summary"

STAGING_DIR=$(mktemp -d)
trap 'rm -rf "$STAGING_DIR"' EXIT

# Download a spec into the staging directory and verify it looks like OpenAPI
download_spec() {
    api="$1"
    url="https://$api.ecosyste.ms/docs/api/v1/openapi.yaml"
    dest="$STAGING_DIR/$api.openapi.yaml"

    if ! curl -fsSL --retry 3 --max-time 60 "$url" -o "$dest"; then
        echo "ERROR: Download failed for $api from $url" >&2
        return 1
    fi

    if [ ! -s "$dest" ]; then
        echo "ERROR: Empty response for $api from $url" >&2
        return 1
    fi

    if ! head -1 "$dest" | grep -Eq '^(---|openapi|info|swagger)'; then
        echo "ERROR: $api does not appear to be a valid OpenAPI spec" >&2
        return 1
    fi

    echo "OK: $api"
}

for api in $APIS; do
    download_spec "$api"
done

# mktemp files are 0600; make the specs world-readable before moving them in
for api in $APIS; do
    chmod 644 "$STAGING_DIR/$api.openapi.yaml"
    mv "$STAGING_DIR/$api.openapi.yaml" "$SPEC_DIR/"
done

# Generate checksums for future verification
shasum -a 256 "$SPEC_DIR"/*.openapi.yaml > "$CHECKSUM_FILE"
echo "Checksums written to $CHECKSUM_FILE"
