# Scholarship Tracker

Proyecto base para un Buscador de Becas con arquitectura de microservicios.

## Estructura

- `.github/workflows/`: CI con GitHub Actions.
- `infra/terraform/`: Plantilla de Infraestructura como Código.
- `backend/`: Microservicio Spring Boot (Java 21, Spring Boot 3.2+).
- `scraper/`: Módulo recolector (placeholder).
- `docs/`: Documentación técnica.

## Backend

Incluye:

- Spring Data JPA + PostgreSQL.
- Spring Validation en entidad `Scholarship`.
- Lombok para reducir boilerplate.
- Separación por capas: Controller, Service y Repository.

## Ejecutar con Docker Compose

Desde la raíz del proyecto:

```bash
docker compose up --build
```

Servicios:

- API: `http://localhost:8080`
- PostgreSQL: `localhost:5432`

## Endpoints base

- `GET /api/v1/scholarships`
- `GET /api/v1/scholarships/{id}`
- `POST /api/v1/scholarships`
- `PUT /api/v1/scholarships/{id}`
- `DELETE /api/v1/scholarships/{id}`
