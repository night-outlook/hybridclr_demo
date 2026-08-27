#!/bin/sh
set -eu
shadow_tool_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
exec python3 "$shadow_tool_dir/shadow_tools.py" pins "$@"
