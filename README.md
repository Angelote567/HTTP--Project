# USJ HTTP Project — Python implementation

From-scratch implementation (TCP sockets only) of an HTTP/1.1 client and server, built by a
team of five students. On top of the mandatory base, the following **optional features**
were added:

| Feature                  | Points | Status |
|--------------------------|--------|--------|
| API key                  | +0.6   | ✅ |
| Logging                  | +0.6   | ✅ |
| Real deployment          | +0.6   | ✅ |
| Cookies                  | +0.6   | ✅ |
| Advanced CRUD            | +0.6   | ✅ |
| Middleware/interceptors  | +0.6   | ✅ |
| Automated testing        | +1.2   | ✅ |

## Team

- Ángel (@Angelote567)
- Blanca
- Sergio
- Jorge
- Mario

## Requirements

- Python 3.11+
- `pytest` to run the automated tests.

## Running the server

```bash
python -m usj_http.server --host 127.0.0.1 --port 8080
```

Available arguments:

| Flag             | Description                                                                          | Alternative environment variable |
|------------------|--------------------------------------------------------------------------------------|----------------------------------|
| `--host`         | Listening host (default `127.0.0.1`).                                                | —                                |
| `--port`         | Listening port (default `8080`).                                                     | —                                |
| `--api-key`      | Optional API key. If set, non-public routes require the `X-API-Key` header.          | `USJ_HTTP_API_KEY`               |
| `--log-file`     | Path to the log file (default `logs/server.log`).                                    | `USJ_HTTP_LOG_FILE`              |
| `--log-level`    | Log level (`DEBUG`, `INFO`, `WARNING`, `ERROR`).                                     | `USJ_HTTP_LOG_LEVEL`             |

Example with all features enabled:

```bash
python -m usj_http.server \
  --host 0.0.0.0 \
  --port 8080 \
  --api-key super-secret-key \
  --log-file logs/server.log \
  --log-level DEBUG
```

## Running the client

Direct CLI mode:

```bash
python -m usj_http.client --url http://127.0.0.1:8080/cats
```

Interactive mode (keeps the cookie jar between requests):

```bash
python -m usj_http.client --interactive
```

If the server requires an API key, pass it with `--api-key` or via the `USJ_HTTP_API_KEY`
environment variable.

## Exposed endpoints

| Method | Path                       | Description                                          |
|--------|----------------------------|------------------------------------------------------|
| GET    | `/` and `/index.html`      | Static page.                                         |
| GET    | `/cats`                    | List of cats.                                        |
| POST   | `/cats`                    | Create a cat (accepts `owner_id`).                   |
| GET    | `/cats/:id`                | Get a cat.                                           |
| PUT    | `/cats/:id`                | Update a cat.                                        |
| DELETE | `/cats/:id`                | Delete a cat.                                        |
| GET    | `/owners`                  | List of owners (advanced CRUD).                      |
| POST   | `/owners`                  | Create an owner.                                     |
| GET    | `/owners/:id`              | Get an owner.                                        |
| PUT    | `/owners/:id`              | Update an owner.                                     |
| DELETE | `/owners/:id`              | Delete an owner. Also cascade-deletes its cats.      |
| GET    | `/owners/:id/cats`         | List the owner's cats (nested resource).             |
| GET    | `/session`                 | Creates/increments a session via cookies.            |
| DELETE | `/session`                 | Ends the session and expires the cookie.             |

Quick examples:

```bash
# Static page
curl http://127.0.0.1:8080/

# List cats of owner 1 (nested resource)
curl http://127.0.0.1:8080/owners/1/cats

# Create a cat linked to an owner
curl -X POST http://127.0.0.1:8080/cats \
  -H "Content-Type: application/json" \
  -d '{"name":"Milo","breed":"Tabby","age":2,"owner_id":1}'

# Authenticated request with API key
curl -H "X-API-Key: super-secret-key" http://127.0.0.1:8080/cats
```

## Automated tests

```bash
python -m pytest
```

They cover basic CRUD, nested resources, validation, status codes, cookies, API key and the
middleware chain. Each test starts a real server on a free port and hits it with the
project's own HTTP client.

## Deployment

The server is deployed in production and publicly accessible at:

**https://http-project-production.up.railway.app**

```bash
# Static page in production
curl https://http-project-production.up.railway.app/

# REST API in production
curl https://http-project-production.up.railway.app/cats

# Using the project's own client
python -m usj_http.client --url https://http-project-production.up.railway.app/cats
```

Build and run the container locally:

```bash
docker build -t usj-http .
docker run --rm -p 8080:8080 usj-http
```

## Package structure

```
usj_http/
├── auth.py             # API key middleware
├── client.py           # HTTP client with cookie jar
├── cookies.py          # Set-Cookie / Cookie helpers and CookieJar
├── http_messages.py    # Request/Response dataclasses and helpers
├── logging_config.py   # Logger configuration + logging middleware
├── middleware.py       # Middleware/interceptor chain
├── parser.py           # HTTP message parser from raw bytes
├── server.py           # Server with routing and dispatcher
├── store.py            # In-memory stores (Cat / Owner / sessions)
└── static/             # Statically served files
```

## Known limitations

- No HTTPS/TLS (that feature was not chosen).
- The connection is closed after each response (`Connection: close`).
- Only bodies with `Content-Length` are parsed, not `Transfer-Encoding: chunked`.
