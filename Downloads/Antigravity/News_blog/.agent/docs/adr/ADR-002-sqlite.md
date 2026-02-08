# ADR-002: SQLite as Database

**Status**: Accepted  
**Date**: 2026-02-08  
**Decision Makers**: Development Team

## Context

We needed a database solution for our News Blog that would:

- Store content (posts, authors, categories, media metadata)
- Support PayloadCMS data requirements
- Be simple to deploy and manage
- Work well for a content-focused application
- Minimize infrastructure complexity
- Support local development easily

### Alternatives Considered

1. **PostgreSQL**
   - ✅ Production-grade, highly scalable
   - ✅ Advanced features (full-text search, JSON queries)
   - ❌ Requires separate database server
   - ❌ More complex deployment
   - ❌ Overkill for current scale

2. **MongoDB**
   - ✅ Flexible schema
   - ✅ PayloadCMS supports it well
   - ❌ Requires separate database server
   - ❌ More complex for relational data
   - ❌ Additional infrastructure cost

3. **MySQL/MariaDB**
   - ✅ Widely supported
   - ✅ Good performance
   - ❌ Requires separate database server
   - ❌ More setup complexity

## Decision

We chose **SQLite** with PayloadCMS's `@payloadcms/db-sqlite` adapter.

### Key Reasons

1. **Zero Configuration**
   - Single file database (`payload.db`)
   - No separate database server needed
   - Works out of the box

2. **Simple Deployment**
   - Deploy database file with application
   - No connection strings or credentials to manage
   - Perfect for serverless/edge deployments

3. **Excellent for Content-Focused Apps**
   - Read-heavy workload (blogs are mostly reads)
   - Sufficient for thousands of posts
   - Fast for our use case

4. **Local Development**
   - Same database in dev and production
   - Easy to reset and seed
   - No Docker/services needed

5. **Backup Simplicity**
   - Backup = copy single file
   - Easy to version control test data
   - Simple disaster recovery

## Consequences

### Positive

✅ **Simplicity**: No database server to manage  
✅ **Cost**: Zero infrastructure cost  
✅ **Performance**: Fast for read-heavy workloads  
✅ **Deployment**: Single file, easy to deploy  
✅ **Development**: Instant setup, no configuration  
✅ **Backup**: Copy file = backup

### Negative

⚠️ **Concurrency**: Limited write concurrency (not an issue for CMS)  
⚠️ **Scalability**: Single file has limits (sufficient for most blogs)  
⚠️ **Features**: No advanced features like full-text search (can add later)  
⚠️ **Replication**: No built-in replication (can use file-level backups)

### Trade-offs Accepted

- **Write Concurrency**: Blog content updates are infrequent, so low write concurrency is acceptable
- **Scalability Ceiling**: If we reach SQLite's limits (unlikely for a blog), we have a clear migration path to PostgreSQL
- **Advanced Features**: We can add full-text search via external services if needed

### Migration Path to PostgreSQL

If we outgrow SQLite, we can migrate to PostgreSQL:

1. **When to Migrate**:
   - Database file exceeds 10GB
   - Need advanced features (full-text search, replication)
   - High concurrent write traffic

2. **Migration Steps**:
   - Export data from SQLite
   - Switch to `@payloadcms/db-postgres`
   - Update `DATABASE_URL` environment variable
   - Import data to PostgreSQL
   - Test thoroughly

3. **Code Changes Required**:
   - Minimal: Only `payload.config.ts` adapter change
   - PayloadCMS abstracts database layer

## Current Configuration

```typescript
// src/payload.config.ts
import { sqliteAdapter } from '@payloadcms/db-sqlite'

export default buildConfig({
  db: sqliteAdapter({
    client: {
      url: process.env.DATABASE_URL || '',
    },
  }),
  // ...
})
```

**Environment Variable**:

```bash
DATABASE_URL=file:./payload.db
```

## Backup Strategy

**Current Approach**:

- Manual: Copy `payload.db` file periodically
- Version control: Test databases in `tests/` directory

**Future Improvements**:

- Automated daily backups to cloud storage
- Point-in-time recovery using SQLite backup API
- Pre-deployment backups in CI/CD pipeline

## Related Decisions

- [ADR-001: PayloadCMS as Headless CMS](./ADR-001-payloadcms.md)
- [ADR-003: Next.js App Router Architecture](./ADR-003-nextjs-architecture.md)

## References

- [SQLite Documentation](https://www.sqlite.org/docs.html)
- [PayloadCMS SQLite Adapter](https://payloadcms.com/docs/database/sqlite)
- [When to Use SQLite](https://www.sqlite.org/whentouse.html)
