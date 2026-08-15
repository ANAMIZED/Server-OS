.PHONY: run build up down verify test mcp cli

run:
	SERVER_OS_LLM_MODE=mock python -c "from server_os.main import run; run()"

mcp:
	PYTHONPATH=src python -m server_os.mcp.server

cli:
	PYTHONPATH=src python -m server_os.cli --help

build:
	docker compose build

up:
	docker compose up --build -d

down:
	docker compose down

verify:
	bash scripts/verify.sh

test:
	PYTHONPATH=src pytest -q
