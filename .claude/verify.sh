#!/usr/bin/env bash
set -e
python3 examples/fixtures/verify_cross_tool_key.py
python3 examples/fixtures/verify_dedup_render.py
