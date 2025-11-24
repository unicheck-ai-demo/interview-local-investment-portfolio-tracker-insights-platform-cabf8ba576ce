# Local Investment Portfolio Tracker & Insights Platform

## Overview
This Django-based backend service provides management for personal and enterprise investment portfolios, with native support for geospatial analytics on financial institutions and high-performance, production-grade API endpoints. Designed for individual investors and small advisory firms, it delivers insights on portfolio performance, asset allocation, and branch proximity using PostGIS, Redis caching, and advanced transaction controls.

## Data Model
### Core Entities
- **User:** Registered account, role-based as Investor or Advisor.
- **Institution:** Represents banks, brokers, and funds, with geospatial location (PostGIS `PointField`, WGS84/SRID=4326).
- **Portfolio:** User-managed collection of assets/trades. Multiple portfolios per user.
- **Asset:** Tracks asset types (stock, bond, mutual fund, local product). Linked to institutions.
- **Transaction:** Records trades, dividends, gains/losses for assets. Time-stamped.

### Relationships
- `User` <-> `Portfolio` (One-to-Many)
- `Portfolio` <-> `Transaction` (One-to-Many)
- `Institution` <-> `Asset` (One-to-Many)
- `Asset` <-> `Transaction` (One-to-Many)

## Features
### Core
- **User Registration/Login:** Role-based, TokenAuthentication and secure session. Endpoints: `/api/register/`, `/api/login/`.
- **Portfolio Management:** Create, edit, delete, and retrieve portfolios per user with atomic update and row-level locking.
- **Asset Tracking:** Manage assets linked to financial institutions, including local investment products.
- **Transaction History & Performance Reports:** Store high-fidelity transaction history; aggregate and analyze using window functions, CTEs.
- **API Endpoints:** Resource-based routing for users, institutions, portfolios, assets, transactions with pagination, filtering, and search support.

### Advanced
- **Branch Locator:** `/api/institutions/nearest/?lat=LAT&lon=LON&radius=KM` — spatial query returns nearest branches via PostGIS, with calculated distances.
- **Multi-Step Transaction Processing:** Ensures database integrity via savepoint/rollback handling for complex transaction flows.
- **Concurrent Portfolio Updates:** Prevent race-conditions with `select_for_update` row-level locking during modification.
- **Portfolio Performance & Summary:** Caching with Redis for high-read endpoints, aggregation with window functions & custom CTE SQL for time-weighted returns.

## Architecture
- **Layered Architecture:**
  - Models: Pure Django ORM, clearly separated from business services.
  - Services: Encapsulate all business logic, transactional boundaries, caching logic.
  - API: DRF ViewSets/Endpoints, always call service layer for business logic, handle permissions.
- **Tech Stack:** Django 4+, DRF, PostgreSQL/PostGIS, Redis, pytest, Docker, Celery (for tasks), Django Environ.
- **Security & Permissions:** Strict per-endpoint permissions, TokenAuthentication enforced except registration/login.
- **Best Practices:** Select_related/prefetch_related avoid N+1 queries; all geospatial data uses SRID=4326; database indexes for frequent lookups.

## Usage Notes
- All geospatial fields expect GeoJSON input or WKT with SRID=4326.
- Portfolio/transaction endpoints are atomic and concurrency-safe.
- Redis is leveraged for caching performance summaries.
- No sensitive information exposed—serializers only return required fields.
- See `/api/docs/` for schema and endpoint details (if enabled).

## Contributing
- Update code only via service layer for business logic, follow patterns as implemented.
- Run `make setup`, `make test`, and `make lint` before submitting PRs. All tests must remain green.

---
Contact: info@unicheck.ai
