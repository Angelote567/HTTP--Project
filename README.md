# Proyecto HTTP de USJ — implementación en Python

Implementación desde cero (solo sockets TCP) de cliente y servidor HTTP/1.1 para la
asignatura de Redes y Comunicaciones.

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

| Flag             | Descripción                                                                            | Variable de entorno alternativa |
|------------------|----------------------------------------------------------------------------------------|---------------------------------|
| `--host`         | Host de escucha (por defecto `127.0.0.1`).                                             | —                               |
| `--port`         | Puerto de escucha (por defecto `8080`).                                                | —                               |
| `--api-key`      | API key opcional. Si se define, las rutas no públicas requieren el header `X-API-Key`. | `USJ_HTTP_API_KEY`              |
| `--log-file`     | Ruta del fichero de log (por defecto `logs/server.log`).                               | `USJ_HTTP_LOG_FILE`             |
| `--log-level`    | Nivel de log (`DEBUG`, `INFO`, `WARNING`, `ERROR`).                                    | `USJ_HTTP_LOG_LEVEL`            |

## Ejecutar el cliente

Modo CLI directo:

```bash
python -m usj_http.client --url http://127.0.0.1:8080/cats
```

Modo interactivo (mantiene la cookie jar entre peticiones):

```bash
python -m usj_http.client --interactive
```

## Endpoints

| Método | Ruta                       | Descripción                                       |
|--------|----------------------------|---------------------------------------------------|
| GET    | `/` y `/index.html`        | Página estática.                                  |
| GET    | `/cats`                    | Lista de gatos.                                   |
| POST   | `/cats`                    | Alta de gato (admite `owner_id`).                 |
| GET    | `/cats/:id`                | Obtener gato.                                     |
| PUT    | `/cats/:id`                | Modificar gato.                                   |
| DELETE | `/cats/:id`                | Borrar gato.                                      |
| GET    | `/owners`                  | Lista de owners.                                  |
| POST   | `/owners`                  | Alta de owner.                                    |
| GET    | `/owners/:id`              | Obtener owner.                                    |
| PUT    | `/owners/:id`              | Modificar owner.                                  |
| DELETE | `/owners/:id`              | Borrar owner. Borra también sus gatos en cascada. |
| GET    | `/owners/:id/cats`         | Listar gatos del owner.                           |
| GET    | `/session`                 | Crea/incrementa una sesión vía cookies.           |
| DELETE | `/session`                 | Cierra la sesión y expira la cookie.              |

## Tests automáticos

```bash
python -m pytest
```

Cubren CRUD básico, recursos anidados, validación, status codes, cookies, API key y la
cadena de middleware. Cada test arranca un servidor real en un puerto libre y le ataca con
el cliente HTTP del propio proyecto.

## Estado

Falta el despliegue real (Docker, VPS, Fly.io) para mañana.
