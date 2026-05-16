# Server deployment

This document describes how to deploy the USJ HTTP server on a public machine.

## Docker image

```bash
docker build -t usj-http .
docker run --rm -p 8080:8080 \
  -e USJ_HTTP_API_KEY=super-secret-key \
  -v "$(pwd)/logs:/app/logs" \
  usj-http
```

The container exposes port 8080 and writes logs to `/app/logs/server.log`, which in this
example is mounted onto `./logs` on the host.

## Deployment on a VPS (Ubuntu / Debian)

1. Install Python 3.11+ and git: `sudo apt install -y python3 python3-pip git`.
2. Clone the project repository.
3. Run the server:

   ```bash
   python3 -m usj_http.server \
     --host 0.0.0.0 \
     --port 8080 \
     --log-file /var/log/usj-http/server.log \
     --api-key "$(openssl rand -hex 16)"
   ```

4. Create a `systemd` service at `/etc/systemd/system/usj-http.service`:

   ```ini
   [Unit]
   Description=USJ HTTP server
   After=network.target

   [Service]
   Type=simple
   WorkingDirectory=/opt/usj_http_project_base
   Environment=USJ_HTTP_API_KEY=super-secret-key
   Environment=USJ_HTTP_LOG_FILE=/var/log/usj-http/server.log
   ExecStart=/usr/bin/python3 -m usj_http.server --host 0.0.0.0 --port 8080
   Restart=on-failure
   User=usjhttp

   [Install]
   WantedBy=multi-user.target
   ```

5. Enable and start: `sudo systemctl enable --now usj-http`.

## Serverless deployment (Fly.io)

Fly.io accepts the `Dockerfile` directly.

```bash
fly launch --copy-config --no-deploy
fly secrets set USJ_HTTP_API_KEY=super-secret-key
fly deploy
```

After deployment, the public URL (`https://<app>.fly.dev`) can be used directly from the
client:

```bash
python -m usj_http.client \
  --url http://<app>.fly.dev/cats \
  --api-key super-secret-key
```

## Real deployment on Railway (production)

The server is permanently deployed on [Railway](https://railway.app), which detects the
repository's `Dockerfile` and builds the image automatically on every push to `main`.
Railway exposes the container port over HTTPS and assigns a stable public URL:

**https://http-project-production.up.railway.app**

Steps followed:

1. Create a project on Railway and link it to the GitHub repository.
2. Railway detects the `Dockerfile` and builds the image (no extra configuration needed).
3. (Optional) Set the `USJ_HTTP_API_KEY` variable in the service's variables panel.
4. Every `git push` to `main` redeploys automatically.

## Verification

Against the real production deployment:

```bash
curl https://http-project-production.up.railway.app/index.html
curl https://http-project-production.up.railway.app/cats
```

Or against a local instance:

```bash
curl http://<host>:8080/index.html
curl -H "X-API-Key: super-secret-key" http://<host>:8080/cats
```

A log line should appear for every received request.
