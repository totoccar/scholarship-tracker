# Arquitectura Base

## Enfoque

Este proyecto sigue una estructura de capas compatible con Clean Architecture a nivel inicial:

- **Controller**: Expone endpoints HTTP.
- **Service**: Encapsula reglas de negocio y coordinación.
- **Repository**: Acceso a datos con Spring Data JPA.
- **Domain/Entity**: Modelo principal del negocio (`Scholarship`).

## Módulos

- `backend/`: API Spring Boot 3.2+ con Java 21.
- `scraper/`: Espacio reservado para recolección de becas.
- `infra/terraform/`: Infraestructura como código.

## Flujo

1. Cliente consume endpoint REST.
2. Controller valida entrada y delega al Service.
3. Service aplica lógica y utiliza Repository.
4. Repository persiste en PostgreSQL.
