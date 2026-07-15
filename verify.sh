#!/bin/bash
# Shell wrapper script to execute python-based report schema verification.

echo "Running output verification checks..."
python scripts/verify.py
exit $?
