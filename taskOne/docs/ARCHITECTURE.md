# BlindSpotX Backend Architecture

## System Overview

BlindSpotX is a multi-tenant platform that combines authentication and drift detection systems into a unified service. The system is built using Flask and follows a modular architecture.

## Core Components

### 1. Authentication System

- JWT-based authentication with HTTP-only cookies
- Role-Based Access Control (RBAC)
- Multi-factor authentication support
- Session management
- Google OAuth integration

### 2. Drift Detection System

- Real-time drift monitoring
- Tenant-scoped data isolation
- Configurable drift thresholds
- Alert system integration

### 3. Multi-tenant Architecture

- Tenant isolation at database level
- Resource quotas per tenant
- Tenant-specific configurations
- Cross-tenant access controls

## Security Architecture

### Authentication & Authorization

- HTTP-only cookies for session management
- JWT tokens with short expiration
- Role-based access control (RBAC)
- Rate limiting per endpoint
- 2FA support for admin accounts

### Data Protection

- Tenant data isolation
- Encrypted data at rest
- Secure session handling
- Input validation and sanitization

### API Security

- Rate limiting
- Request validation
- CORS configuration
- API key management

## Database Schema

### Users Collection

```json
{
  "email": "string",
  "password": "string (hashed)",
  "role": "string",
  "tenant_id": "string",
  "2fa_enabled": "boolean",
  "2fa_secret": "string",
  "created_at": "datetime",
  "last_login": "datetime"
}
```

### Tenants Collection

```json
{
  "tenant_id": "string",
  "name": "string",
  "settings": "object",
  "quota": "object",
  "created_at": "datetime"
}
```

### Drift Configurations Collection

```json
{
  "tenant_id": "string",
  "config_id": "string",
  "thresholds": "object",
  "alerts": "array",
  "created_at": "datetime"
}
```

## API Endpoints

### Authentication

- POST /api/auth/login
- POST /api/auth/google-login
- POST /api/auth/2fa/verify
- POST /api/auth/logout

### User Management

- GET /api/users
- POST /api/users
- PUT /api/users/{id}
- DELETE /api/users/{id}

### Tenant Management

- GET /api/tenants
- POST /api/tenants
- PUT /api/tenants/{id}
- DELETE /api/tenants/{id}

### Drift Management

- GET /api/drift/configs
- POST /api/drift/configs
- PUT /api/drift/configs/{id}
- GET /api/drift/alerts

## Security Considerations

### Session Management

- HTTP-only cookies for session storage
- Secure cookie attributes
- Session timeout configuration
- Session invalidation on logout

### Rate Limiting

- Per-endpoint rate limits
- IP-based rate limiting
- Tenant-based rate limiting
- Burst allowance configuration

### Data Protection

- Input validation
- Output encoding
- SQL injection prevention
- XSS protection
- CSRF protection

### Monitoring & Logging

- Security event logging
- Audit trails
- Performance monitoring
- Error tracking
