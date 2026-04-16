#!/bin/sh

set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
REPO_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)
DEFAULT_SOURCE="$REPO_ROOT/../ha_wf_card/ha_wf_card.js"
SOURCE_PATH="${1:-$DEFAULT_SOURCE}"
TARGET_PATH="$REPO_ROOT/custom_components/windfinder/ha_wf_card.js"

if [ ! -f "$SOURCE_PATH" ]; then
  echo "Source card file not found: $SOURCE_PATH" >&2
  echo "Usage: $0 [path-to-ha_wf_card.js]" >&2
  exit 1
fi

cp "$SOURCE_PATH" "$TARGET_PATH"
echo "Synced $SOURCE_PATH -> $TARGET_PATH"
