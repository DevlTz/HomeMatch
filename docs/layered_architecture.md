# Layered Architecture Guide

This project follows a Spring-style layered architecture:

- GUI/API layer: Django/DRF `views`, `urls`, and serializers for input/output shape.
- Service layer: use-case orchestration and business rules.
- Data layer: model persistence and data access helpers (repositories).

## Layer Responsibilities

### GUI/API Layer

- Receives HTTP requests and returns HTTP responses.
- Validates payload shape using serializers.
- Must delegate business workflows to services.
- Must not orchestrate multi-step ORM workflows directly.

### Service Layer

- Implements business use-cases and process orchestration.
- May compose multiple repositories and external adapters.
- Must not import DRF `Request`, `Response`, view classes, or HTTP primitives.

### Data Layer

- Encapsulates ORM operations and query logic.
- Exposes repository functions used by services.
- Keeps model constraints as the final integrity guard.

## Practical Rules

1. Views/serializers do validation and delegation, not business orchestration.
2. Services coordinate workflows and business decisions.
3. Repositories isolate ORM query details from services.
4. External integrations (cloud storage, AI providers) are used from services.
5. Hidden side-effects in signals should be avoided for core workflows.
