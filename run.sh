#!/bin/bash
# shellcheck disable=SC2086

LOG_FILE="./static/hidden/latest.log"
LOG_DIR="./static/hidden"

if [ -f "$LOG_FILE" ]; then
    TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
    mv "$LOG_FILE" "$LOG_DIR/run_${TIMESTAMP}.log"
    echo "run_${TIMESTAMP}.log is ready."
fi

DEFAULT_ARGS="--debug --extra"
USER_ARGS=""
if [ -f "user_args.txt" ]; then
    USER_ARGS=$(grep -vE '^\s*#' user_args.txt | grep -vE '^\s*$' | head -1)
fi

if [ -z "$USER_ARGS" ]; then
    USER_ARGS="$DEFAULT_ARGS"
fi
python app.py $USER_ARGS 2>&1 | tee "$LOG_FILE"