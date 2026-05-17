# USJ HTTP Project

From-scratch HTTP/1.1 client and server in Python, using only TCP sockets and the
standard library. Built by a team of five students for the Networks and Communications
course.

Live deployment: https://http-project-production.up.railway.app

## Team

Ángel (@Angelote567), Blanca, Sergio, Jorge and Mario.

## Requirements

Python 3.11+ (and `pytest` to run the tests).

## Running the server

```bash
python -m usj_http.server --host 127.0.0.1 --port 8080
```

Optional flags: `--api-key`, `--log-file`, `--log-level` (also configurable via the
`USJ_HTTP_API_KEY`, `USJ_HTTP_LOG_FILE` and `USJ_HTTP_LOG_LEVEL` environment variables).

## Running the client

```bash
python -m usj_http.client --url http://127.0.0.1:8080/cats
python -m usj_http.client --interactive
```

## Endpoints

A small REST API over cats and owners, plus a static page and cookie sessions:

- `GET /` — static page
- `GET/POST /cats` and `GET/PUT/DELETE /cats/:id` — cats CRUD
- `GET/POST /owners` and `GET/PUT/DELETE /owners/:id` — owners CRUD (deleting an owner
  cascades to its cats)
- `GET /owners/:id/cats` — nested resource
- `GET/DELETE /session` — cookie-based session

Example:

```bash
curl http://127.0.0.1:8080/cats
curl -X POST http://127.0.0.1:8080/cats \
  -H "Content-Type: application/json" \
  -d '{"name":"Milo","breed":"Tabby","age":2,"owner_id":1}'
```

## Tests

```bash
python -m pytest
```

## Deployment

The server runs in production on Railway, built from the `Dockerfile` in this repository:

https://http-project-production.up.railway.app

```bash
curl https://http-project-production.up.railway.app/cats
```

## Known limitations

No HTTPS/TLS, one request per connection (`Connection: close`), and only
`Content-Length` bodies are parsed (no chunked transfer encoding).
