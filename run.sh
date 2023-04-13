#!/bin/bash
DMCompiler environment.dme
OpenDreamServer --config-file server_config.toml --cvar opendream.json_path=/app/environment.json | cat