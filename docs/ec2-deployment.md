# Deploying the Demo Gateway to AWS EC2

This repository can run on EC2 for a demo or internal proof of concept. It is
not production-hardened yet.

## Minimal EC2 Demo

1. Launch an Ubuntu EC2 instance.
2. Attach a security group that allows SSH from your IP and HTTP access to the
   selected demo port, for example `8000`.
3. Install Python 3.12 or newer and Git.
4. Clone the repository.
5. Install the app:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
```

6. For fake-provider demos, leave `AMG_ENABLE_OPENAI=false`.
7. For real OpenAI calls, set:

```bash
OPENAI_API_KEY=sk-...
APP_ENV=development
```

`AMG_ENABLE_OPENAI=true` is optional when `OPENAI_API_KEY` is present. Set
`AMG_ENABLE_OPENAI=false` only when you want to force fake-provider routing.

8. Run the API:

```bash
amg serve --host 0.0.0.0 --port 8000 --no-reload
```

9. Test from your laptop:

```bash
curl http://EC2_PUBLIC_IP:8000/health
```

## Better EC2 Shape

For a stronger demo, put Nginx or an AWS Application Load Balancer in front of
the app, terminate TLS there, and run Uvicorn under `systemd` so the process
restarts after instance reboot.

Example service shape:

```ini
[Unit]
Description=Agent Model Gateway
After=network.target

[Service]
WorkingDirectory=/opt/agent-model-gateway
EnvironmentFile=/opt/agent-model-gateway/.env
ExecStart=/opt/agent-model-gateway/.venv/bin/uvicorn app.api:app --host 0.0.0.0 --port 8000
Restart=always
User=amg

[Install]
WantedBy=multi-user.target
```

## Production Gaps

Before exposing this as a production service, add:

- Authentication and authorization.
- TLS, either at ALB/Nginx or directly in the serving layer.
- Secret management through AWS Secrets Manager or SSM Parameter Store.
- Structured logging with prompt and secret redaction.
- Request IDs, tracing, and metrics.
- Rate limits and quotas.
- Provider retry, timeout, and circuit-breaker policy.
- Persistent versioned registries for agents, profiles, and models.
- A durable workflow engine for multi-step agents and tool calls.
- A real policy layer for writes, data classification, and tool permissions.
