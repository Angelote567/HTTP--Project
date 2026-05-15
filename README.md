# Proyecto HTTP de USJ — implementación en Python

Implementación desde cero (solo sockets TCP) de cliente y servidor HTTP/1.1 para el grupo de cinco
estudiantes. Sobre la base obligatoria se han añadido las siguientes **features opcionales**:

| Feature                  | Puntos | Estado |
|--------------------------|--------|--------|
| API key                  | +0.6   | ✅ |
| Logging                  | +0.6   | ✅ |
| Despliegue real          | +0.6   | ✅ |
| Cookies                  | +0.6   | ✅ |
| CRUD avanzado            | +0.6   | ✅ |
| Middleware/interceptores | +0.6   | ✅ |
| Testing automático       | +1.2   | ✅ |

## Equipo

- Ángel (@Angelote567)
- Blanca
- Sergio
- Jorge
- Mario

## Requisitos

- Python 3.11+
- `pytest` para ejecutar los tests automáticos.

## Ejecutar el servidor

```bash
python -m usj_http.server --host 127.0.0.1 --port 8080
```

Argumentos disponibles:

| Flag             | Descripción                                                              | Variable de entorno alternativa |
|------------------|--------------------------------------------------------------------------|---------------------------------|
| `--host`         | Host de escucha (por defecto `127.0.0.1`).                               | —                               |
| `--port`         | Puerto de escucha (por defecto `8080`).                                  | —                               |
| `--api-key`      | API key opcional. Si se define, las rutas no públicas requieren el header `X-API-Key`. | `USJ_HTTP_API_KEY`              |
| `--log-file`     | Ruta del fichero de log (por defecto `logs/server.log`).                 | `USJ_HTTP_LOG_FILE`             |
| `--log-level`    | Nivel de log (`DEBUG`, `INFO`, `WARNING`, `ERROR`).                      | `USJ_HTTP_LOG_LEVEL`            |

Ejemplo con todas las features activas:

```bash
python -m usj_http.server \
  --host 0.0.0.0 \
  --port 8080 \
  --api-key clave-super-secreta \
  --log-file logs/server.log \
  --log-level DEBUG
```

## Ejecutar el cliente

Modo CLI directo:

```bash
python -m usj_http.client --url http://127.0.0.1:8080/cats
```

Modo interactivo (mantiene la cookie jar entre peticiones):

```bash
python -m usj_http.client --interactive
```

Si el servidor exige API key, se pasa con `--api-key` o por la variable `USJ_HTTP_API_KEY`.

## Endpoints expuestos

| Método | Ruta                       | Descripción                                                  |
|--------|----------------------------|--------------------------------------------------------------|
| GET    | `/` y `/index.html`        | Página estática.                                            |
| GET    | `/cats`                    | Lista de gatos.                                              |
| POST   | `/cats`                    | Alta de gato (admite `owner_id`).                            |
| GET    | `/cats/:id`                | Obtener gato.                                                |
| PUT    | `/cats/:id`                | Modificar gato.                                              |
| DELETE | `/cats/:id`                | Borrar gato.                                                 |
| GET    | `/owners`                  | Lista de owners (CRUD avanzado).                             |
| POST   | `/owners`                  | Alta de owner.                                               |
| GET    | `/owners/:id`              | Obtener owner.                                               |
| PUT    | `/owners/:id`              | Modificar owner.                                             |
| DELETE | `/owners/:id`              | Borrar owner. Borra también sus gatos en cascada.            |
| GET    | `/owners/:id/cats`         | Listar gatos del owner (recurso anidado).                    |
| GET    | `/session`                 | Crea/incrementa una sesión vía cookies.                      |
| DELETE | `/session`                 | Cierra la sesión y expira la cookie.                         |

Ejemplos rápidos:

```bash
# Página estática
curl http://127.0.0.1:8080/

# Listar gatos del owner 1 (recurso anidado)
curl http://127.0.0.1:8080/owners/1/cats

# Crear gato asociado a un owner
curl -X POST http://127.0.0.1:8080/cats \
  -H "Content-Type: application/json" \
  -d '{"name":"Milo","breed":"Tabby","age":2,"owner_id":1}'

# Petición autenticada con API key
curl -H "X-API-Key: clave-super-secreta" http://127.0.0.1:8080/cats
```

## Tests automáticos

```bash
python -m pytest
```

Cubren CRUD básico, recursos anidados, validación, status codes, cookies, API key y la cadena
de middleware. Cada test arranca un servidor real en un puerto libre y le ataca con el cliente
HTTP del propio proyecto.

## Despliegue

El servidor está desplegado en producción y accesible públicamente en:

**https://http-project-production.up.railway.app**

```bash
# Página estática en producción
curl https://http-project-production.up.railway.app/

# API REST en producción
curl https://http-project-production.up.railway.app/cats

# Desde el propio cliente del proyecto
python -m usj_http.client --url https://http-project-production.up.railway.app/cats
```

Ver [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md) para el detalle. Incluye `Dockerfile`,
despliegue real en Railway, instrucciones para VPS con `systemd` y un ejemplo en Fly.io.

```bash
docker build -t usj-http .
docker run --rm -p 8080:8080 usj-http
```

## Estructura del paquete

```
usj_http/
├── auth.py             # Middleware de API key
├── client.py           # Cliente HTTP con cookie jar
├── cookies.py          # Helpers de Set-Cookie / Cookie y CookieJar
├── http_messages.py    # Dataclasses Request/Response y helpers
├── logging_config.py   # Configuración de logger + middleware de logs
├── middleware.py       # Cadena de middleware/interceptores
├── parser.py           # Parser de mensajes HTTP a partir de bytes
├── server.py           # Servidor con routing y dispatcher
├── store.py            # Stores en memoria (Cat / Owner / sesiones)
└── static/             # Ficheros servidos estáticamente
```

## Limitaciones conocidas

- No hay HTTPS/TLS (no se ha optado por esa feature).
- Conexión cerrada tras cada respuesta (`Connection: close`).
- Solo se parsean cuerpos con `Content-Length`, no `Transfer-Encoding: chunked`.
