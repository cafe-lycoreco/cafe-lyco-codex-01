.PHONY: check status

check:
	python3 scripts/check_workspace.py

status:
	git status --short --branch
