#!/bin/bash
cp /app/code/* .
DMCompiler test.dme
OpenDreamServer --config-file server_config.toml --cvar opendream.json_path=/app/test.json | cat
