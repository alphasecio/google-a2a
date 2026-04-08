# Google A2A

A collection of [A2A protocol](https://google.github.io/A2A/) agents and clients. Deploy on Google [Cloud Run](https://cloud.google.com/run) or [Railway](https://railway.app/?referralCode=alphasec).

## Structure

```
├── server/
│   ├── hello_apikey/   # Public hello + API-key-authenticated dice rolling
│   └── hello_oauth/    # Public hello + OAuth-authenticated dice rolling
└── client/
    ├── streamlit_app.py        # Web GUI client (supports API key + OAuth 2.0)
    ├── hello_apikey_client.py  # CLI test client (API key)
    └── hello_oauth_client.py   # CLI test client (OAuth 2.0)
```

## Quick Start

```bash
# Server (API key)
cd server/hello_apikey && cp .env.example .env
uv run python __main__.py

# Server (OAuth 2.0)
cd server/hello_oauth && cp .env.example .env
uv run python __main__.py

# Client
cd client && cp .env.example .env
streamlit run streamlit_app.py
```

## Servers

| Name | Path | Auth | Deploy |
|------|------|------|--------|
| Hello (API Key) | `server/hello_apikey` | Static Bearer token | Railway |
| Hello (OAuth) | `server/hello_oauth` | OAuth 2.0 JWT | Cloud Run |

## Clients

| Name | Description |
|------|-------------|
| `streamlit_app.py` | Web GUI — supports None, API key, and OAuth auth |
| `hello_apikey_client.py` | CLI smoke test for API key server |
| `hello_oauth_client.py` | CLI smoke test for OAuth server |
