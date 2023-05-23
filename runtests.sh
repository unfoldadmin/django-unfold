#!/bin/bash
# Set the RANDOM_SEED environment variable, to keep the tests deterministic between different environments

# If RANDOM_SEED is not set or is empty
if [[ -z "${RANDOM_SEED}" ]]; then
    export RANDOM_SEED=$((( RANDOM % 10000 ) + 1)) # Generate a random number between 1 and 10000
fi

echo "Running tests with RANDOM_SEED=$RANDOM_SEED"
tox
