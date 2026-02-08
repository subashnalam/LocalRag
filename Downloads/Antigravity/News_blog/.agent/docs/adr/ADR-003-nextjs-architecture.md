# ADR-003: Next.js App Router Architecture

**Status**: Accepted  
**Date**: 2026-02-08  
**Decision Makers**: Development Team

## Context

We needed to structure our Next.js application to:

- Separate frontend (public blog) from backend (PayloadCMS admin)
- Leverage Next.js 15 App Router features
- Optimize for performance (Server Components, streaming)
- Maintain clear boundaries between concerns
- Enable future scalability

### Alternatives Considered

1. **Pages Router**
   - ✅ Mature and stable
   - ❌ Older architecture
   - ❌ No Server Components
   - ❌ Less optimal data fetching

2. **Separate Frontend and Backend Apps**
   - ✅ Complete separation
   - ❌ Two deployments to manage
   - ❌ More complex infrastructure
   - ❌ Slower development

3. **Monolithic App Router**
   - ✅ Simple structure
   - ❌ No clear separation
   - ❌ Harder to maintain
   - ❌ Mixing concerns

## Decision

We chose **Next.js App Router with Route Groups** to separate frontend and admin.

### Architecture Overview

```
src/app/
├── (frontend)/          # Public blog routes
│   ├── page.tsx         # Homepage
│   ├── posts/[slug]/    # Individual post pages
│   ├── category/[slug]/ # Category pages
│   ├── components/      # Frontend components
│   ├── utils.ts         # Frontend utilities
│   └── layout.tsx       # Frontend layout
│
└── (payload)/           # PayloadCMS admin routes
    ├── admin/           # Admin panel
    ├── api/             # API routes
    └── layout.tsx       # Admin layout
```

### Key Architectural Decisions

#### 1. Route Groups for Separation

**Pattern**: Use `(frontend)` and `(payload)` route groups

**Benefits**:

- Clear separation of concerns
- Different layouts for blog vs admin
- Easy to apply middleware selectively
- Prevents route conflicts

**Example**:

```typescript
// (frontend)/layout.tsx - Public blog layout
export default function FrontendLayout({ children }) {
  return (
    <>
      <Header />
      {children}
      <Footer />
    </>
  )
}

// (payload)/layout.tsx - Admin layout
export default function PayloadLayout({ children }) {
  return children // PayloadCMS provides its own layout
}
```

#### 2. Server Components as Default

**Pattern**: All components are Server Components unless they need client-side interactivity

**Benefits**:

- Zero JavaScript for static content
- Faster page loads
- Better SEO
- Direct database access

**When to Use Client Components**:

- State management (`useState`, `useReducer`)
- Effects (`useEffect`)
- Event handlers (`onClick`, `onChange`)
- Browser APIs (`localStorage`, `window`)

**Example**:

```typescript
// ✅ Server Component (default)
export default async function PostPage({ params }) {
  const payload = await getPayload({ config })
  const post = await payload.findByID({
    collection: 'posts',
    id: params.slug,
  })

  return <PostContent post={post} />
}

// ✅ Client Component (when needed)
'use client'
export function SearchBar() {
  const [query, setQuery] = useState('')
  return <input value={query} onChange={(e) => setQuery(e.target.value)} />
}
```

#### 3. Data Fetching at Page Level

**Pattern**: Fetch data in Server Components close to where it's used

**Benefits**:

- Next.js deduplicates `fetch` requests
- No prop drilling needed
- Parallel data fetching
- Streaming with Suspense

**Example**:

```typescript
// ✅ Good: Fetch in page component
export default async function HomePage() {
  const payload = await getPayload({ config })

  // These run in parallel automatically
  const [posts, categories] = await Promise.all([
    payload.find({ collection: 'posts' }),
    payload.find({ collection: 'categories' }),
  ])

  return <PostList posts={posts.docs} categories={categories.docs} />
}
```

#### 4. Dynamic Route Configuration

**Pattern**: Use `export const dynamic = 'force-dynamic'` for CMS content

**Reason**: Content can change in PayloadCMS admin, so we need fresh data

**Example**:

```typescript
// Ensure page always fetches fresh data
export const dynamic = 'force-dynamic'

export default async function HomePage() {
  // Always fetches latest posts
  const posts = await fetchPosts()
  return <PostList posts={posts} />
}
```

## Consequences

### Positive

✅ **Clear Separation**: Frontend and admin are logically separated  
✅ **Performance**: Server Components reduce JavaScript bundle  
✅ **SEO**: Server-side rendering for all content  
✅ **Developer Experience**: Modern React patterns  
✅ **Scalability**: Easy to split into separate apps later  
✅ **Type Safety**: TypeScript throughout

### Negative

⚠️ **Learning Curve**: Team needs to understand Server vs Client Components  
⚠️ **Debugging**: Server Component errors can be harder to debug  
⚠️ **Caching**: Need to understand Next.js caching behavior

### Best Practices Established

1. **Default to Server Components**: Only add `'use client'` when necessary
2. **Parallel Data Fetching**: Use `Promise.all` for independent requests
3. **Utility Functions**: Extract complex logic to testable utilities
4. **Error Boundaries**: Add error handling for graceful failures
5. **Loading States**: Use Suspense boundaries for better UX

## File Organization Conventions

### Frontend Components

```
(frontend)/
├── components/
│   ├── Header.tsx        # Site header
│   ├── Footer.tsx        # Site footer
│   └── PostCard.tsx      # Reusable post card
├── utils.ts              # Pure utility functions
└── styles.css            # Global styles
```

### Utility Functions Pattern

**Rule**: Extract complex logic to `utils.ts` for testability

```typescript
// utils.ts - Pure, testable functions
export function getHeroImageUrl(heroImage: Post['heroImage']): string | null {
  if (typeof heroImage === 'object' && heroImage !== null && 'url' in heroImage) {
    return heroImage.url || null
  }
  return null
}

// page.tsx - Use utilities in components
import { getHeroImageUrl } from './utils'

export default async function PostPage({ params }) {
  const post = await fetchPost(params.slug)
  const imageUrl = getHeroImageUrl(post.heroImage)
  return <img src={imageUrl} alt={post.title} />
}
```

## Related Decisions

- [ADR-001: PayloadCMS as Headless CMS](./ADR-001-payloadcms.md)
- [ADR-004: Testing Strategy](./ADR-004-testing-strategy.md)

## References

- [Next.js App Router Documentation](https://nextjs.org/docs/app)
- [Server Components](https://nextjs.org/docs/app/building-your-application/rendering/server-components)
- [Route Groups](https://nextjs.org/docs/app/building-your-application/routing/route-groups)
