#!/bin/bash
cd "$(dirname "$0")"
if [ $# -eq 0 ]; then
    ./run.sh --vfs vfs_samples/full.json
else
    ./run.sh "$@"
fi
