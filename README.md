# Proyecto HTTP de USJ — implementación en Python

Implementación desde cero (solo sockets TCP) de cliente y servidor HTTP/1.1 para la
asignatura de Redes y Comunicaciones.

## Requisitos

- Python 3.11+

## Ejecutar el servidor

```bash
python -m usj_http.server --host 127.0.0.1 --port 8080
```

## Endpoints

| Método | Ruta                       | Descripción                                       |
|--------|----------------------------|---------------------------------------------------|
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

## Estado

En desarrollo. Cliente, autenticación, cookies, middleware y tests se irán añadiendo.
