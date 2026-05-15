# Despliegue del servidor

Este documento describe cómo desplegar el servidor HTTP de USJ en una máquina pública.

## Imagen Docker

```bash
docker build -t usj-http .
docker run --rm -p 8080:8080 \
  -e USJ_HTTP_API_KEY=clave-super-secreta \
  -v "$(pwd)/logs:/app/logs" \
  usj-http
```

El contenedor expone el puerto 8080 y escribe los logs en `/app/logs/server.log`,
que en el ejemplo se monta sobre `./logs` del host.

## Despliegue en una VPS (Ubuntu / Debian)

1. Instalar Python 3.11+ y git: `sudo apt install -y python3 python3-pip git`.
2. Clonar el repositorio del proyecto.
3. Ejecutar el servidor:

   ```bash
   python3 -m usj_http.server \
     --host 0.0.0.0 \
     --port 8080 \
     --log-file /var/log/usj-http/server.log \
     --api-key "$(openssl rand -hex 16)"
   ```

4. Crear un servicio `systemd` en `/etc/systemd/system/usj-http.service`:

   ```ini
   [Unit]
   Description=USJ HTTP server
   After=network.target

   [Service]
   Type=simple
   WorkingDirectory=/opt/usj_http_project_base
   Environment=USJ_HTTP_API_KEY=clave-super-secreta
   Environment=USJ_HTTP_LOG_FILE=/var/log/usj-http/server.log
   ExecStart=/usr/bin/python3 -m usj_http.server --host 0.0.0.0 --port 8080
   Restart=on-failure
   User=usjhttp

   [Install]
   WantedBy=multi-user.target
   ```

5. Habilitar e iniciar: `sudo systemctl enable --now usj-http`.

## Despliegue serverless (Fly.io)

Fly.io acepta el `Dockerfile` directamente.

```bash
fly launch --copy-config --no-deploy
fly secrets set USJ_HTTP_API_KEY=clave-super-secreta
fly deploy
```

Tras el despliegue, la URL pública (`https://<app>.fly.dev`) se puede usar
directamente desde el cliente:

```bash
python -m usj_http.client \
  --url http://<app>.fly.dev/cats \
  --api-key clave-super-secreta
```

## Comprobación

Una vez en marcha:

```bash
curl http://<host>:8080/index.html
curl -H "X-API-Key: clave-super-secreta" http://<host>:8080/cats
```

Y en el log debe aparecer una línea por cada petición recibida.
