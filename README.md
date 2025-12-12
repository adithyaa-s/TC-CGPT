TrainerCentral FastAPI wrapper
=============================

This repository contains a FastAPI wrapper around TrainerCentral library modules.

Quick start
-----------

1. Create a Python virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Set required environment variables for OAuth (Zoho):

```bash
export CLIENT_ID="<your_client_id>"
export CLIENT_SECRET="<your_client_secret>"
export REFRESH_TOKEN="<your_refresh_token>"
export ORG_ID="<your_org_id>"
export DOMAIN="https://training.example.com"  # your TrainerCentral domain
```

3. Run the FastAPI app:

```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

4. Open docs: http://localhost:8000/docs

OAuth notes
-----------

- The OAuth helper is available at `utils/oauth.py` as `ZohoOAuth`.
- It expects `CLIENT_ID`, `CLIENT_SECRET`, and `REFRESH_TOKEN` in the environment.
- The library modules call `ZohoOAuth.get_access_token()` to get a valid token before making API calls.

Security
--------

Do not commit your OAuth credentials or refresh tokens to source control. Use environment variables or a secrets manager.

Next steps
----------
- I can finish removing the leftover `tools/` MCP code from the repo (it is currently present). Confirm if you want me to delete it now.
- Optionally I can add an endpoint to validate and return a fresh access token for local testing (not recommended for production).
