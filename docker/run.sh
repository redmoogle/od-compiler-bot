#!/bin/sh
cp /app/code/* .
echo "---Preamble---"
echo Included compiler arguments: "$@"
echo "---Start Compiler---"
DMCompiler "$@" test.dme
echo "---End Compiler---"
echo "---Start Server---"
OpenDreamServer --config-file server_config.toml --cvar opendream.json_path=/app/test.json
echo "---End Server---"
