# ADR-001: PayloadCMS as Headless CMS

**Status**: Accepted  
**Date**: 2026-02-08  
**Decision Makers**: Development Team

## Context

We needed a headless CMS solution for our News Blog that would:

- Provide a user-friendly admin interface for content management
- Support TypeScript for type safety
- Allow self-hosting for full control and cost efficiency
- Work seamlessly with Next.js
- Support SQLite for simple deployment
- Provide flexible content modeling (posts, authors, categories, media)

### Alternatives Considered

1. **Strapi**
   - ✅ Popular open-source headless CMS
   - ❌ More complex setup
   - ❌ Heavier resource requirements

2. **Sanity**
   - ✅ Great developer experience
   - ❌ Cloud-hosted (vendor lock-in)
   - ❌ Pricing scales with usage

3. **Contentful**
   - ✅ Mature platform
   - ❌ Expensive for production
   - ❌ Limited free tier

4. **Custom REST API**
   - ✅ Full control
   - ❌ Need to build admin UI from scratch
   - ❌ Significant development time

## Decision

We chose **PayloadCMS** (v3.73.0) as our headless CMS.

### Key Reasons

1. **TypeScript-Native**
   - Auto-generates TypeScript types from collections (`payload-types.ts`)
   - Full type safety between CMS and frontend
   - Better IDE autocomplete and error detection

2. **Self-Hosted with SQLite Support**
   - No vendor lock-in
   - Works with SQLite for simple deployment
   - Can migrate to PostgreSQL if needed
   - Full control over data

3. **Built-in Admin UI**
   - Professional admin panel out of the box
   - Customizable with React components
   - Role-based access control
   - Media management included

4. **Next.js Integration**
   - Official `@payloadcms/next` package
   - Shares the same Next.js server
   - No separate backend server needed
   - Optimal performance

5. **Flexible Content Modeling**
   - Collections for Posts, Authors, Categories, Media
   - Rich relationship system
   - Upload fields for media
   - Lexical rich text editor

## Consequences

### Positive

✅ **Type Safety**: Auto-generated types prevent runtime errors  
✅ **Developer Experience**: Excellent DX with TypeScript and Next.js  
✅ **Cost**: Free and self-hosted  
✅ **Control**: Full ownership of data and infrastructure  
✅ **Admin UI**: Professional interface without custom development  
✅ **Scalability**: Can migrate from SQLite to PostgreSQL when needed

### Negative

⚠️ **Learning Curve**: Team needs to learn PayloadCMS-specific patterns  
⚠️ **Community Size**: Smaller community compared to Strapi/Contentful  
⚠️ **Self-Hosting**: We're responsible for deployment and maintenance  
⚠️ **Version Updates**: Need to manage PayloadCMS version upgrades

### Mitigation Strategies

- **Documentation**: Create custom Antigravity skill for PayloadCMS patterns
- **Testing**: Comprehensive integration tests for all collections
- **Deployment**: Document deployment process and backup strategy
- **Monitoring**: Set up error tracking and performance monitoring

## Related Decisions

- [ADR-002: SQLite Database](./ADR-002-sqlite.md)
- [ADR-003: Next.js App Router Architecture](./ADR-003-nextjs-architecture.md)

## References

- [PayloadCMS Documentation](https://payloadcms.com/docs)
- [PayloadCMS GitHub](https://github.com/payloadcms/payload)
- [Next.js Integration Guide](https://payloadcms.com/docs/getting-started/installation#nextjs)
