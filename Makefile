.PHONY: dashboard dashboard-dev

# Serve the Panel dashboard
dashboard:
	uv run --package dashboard dashboard --show

# Serve the dashboard with auto-reload on code changes
dashboard-dev:
	uv run --package dashboard dashboard --dev --show
