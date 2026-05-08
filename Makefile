.PHONY: help install install-local run

help:
	@echo "cubicle helpers"
	@echo ""
	@echo "make install"
	@echo "  Mark ./cubicle as executable"
	@echo ""
	@echo "make install-local"
	@echo "  Install cubicle from this repo into the active Python environment"
	@echo ""
	@echo "make run AGENT=<codex|claude|copilot|gemini> PROJECT=<name>"
	@echo "  Run the selected agent for a project"

install:
	@chmod +x ./cubicle
	@echo "Marked ./cubicle as executable"

install-local:
	@uv pip install -e .
	@echo "Installed cubicle from local source"

run:
	@[ -n "$(AGENT)" ] || (echo "Missing AGENT"; exit 1)
	@[ -n "$(PROJECT)" ] || (echo "Missing PROJECT"; exit 1)
	@./cubicle run --agent "$(AGENT)" --project "$(PROJECT)"
