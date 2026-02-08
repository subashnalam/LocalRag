---
description: Data fetching patterns for Next.js 15 + PayloadCMS integration in the News Blog project.
---

# Data Fetching Patterns

You are working with Next.js 15 App Router and PayloadCMS. Follow these patterns for optimal performance and maintainability.

## 🎯 Core Principles

1. **Server Components First**: Fetch data in Server Components by default
2. **Parallel Fetching**: Use `Promise.all` for independent requests
3. **Error Handling**: Always handle errors gracefully
4. **Loading States**: Use Suspense boundaries for better UX
5. **Query Optimization**: Minimize over-fetching with `depth` and `select`

---

## 🏗️ Server Component Data Fetching

### Basic Pattern

**Rule**: Fetch data in Server Components (no `'use client'` directive)

```typescript
// ✅ Good: Server Component with data fetching
import { getPayload } from 'payload'
import config from '@/payload.config'

export default async function PostPage({ params }: { params: { slug: string } }) {
  const payload = await getPayload({ config })

  const post = await payload.findByID({
    collection: 'posts',
    id: params.slug,
  })

  return <PostContent post={post} />
}
```

### Dynamic Route Configuration

**Rule**: Use `export const dynamic = 'force-dynamic'` for CMS content

**Why**: Content can change in PayloadCMS admin, so we need fresh data

```typescript
// Force dynamic rendering for fresh CMS data
export const dynamic = 'force-dynamic'

export default async function HomePage() {
  const posts = await fetchPosts() // Always fetches latest
  return <PostList posts={posts} />
}
```

---

## ⚡ Parallel Fetching

### The Waterfall Problem

**❌ Bad: Sequential fetching (slow)**

```typescript
export default async function HomePage() {
  const payload = await getPayload({ config })

  // These run sequentially - SLOW!
  const posts = await payload.find({ collection: 'posts' })
  const categories = await payload.find({ collection: 'categories' })
  const authors = await payload.find({ collection: 'authors' })

  // Total time: T1 + T2 + T3
  return <HomePage posts={posts} categories={categories} authors={authors} />
}
```

### The Solution: Promise.all

**✅ Good: Parallel fetching (fast)**

```typescript
export default async function HomePage() {
  const payload = await getPayload({ config })

  // These run in parallel - FAST!
  const [posts, categories, authors] = await Promise.all([
    payload.find({ collection: 'posts' }),
    payload.find({ collection: 'categories' }),
    payload.find({ collection: 'authors' }),
  ])

  // Total time: max(T1, T2, T3)
  return <HomePage posts={posts} categories={categories} authors={authors} />
}
```

### Real-World Example

```typescript
// src/app/(frontend)/page.tsx
export const dynamic = 'force-dynamic'

export default async function HomePage() {
  const payload = await getPayload({ config })

  // Fetch posts and categories in parallel
  const [postsResult, categoriesResult] = await Promise.all([
    payload.find({
      collection: 'posts',
      sort: '-publishedDate',
      limit: 10,
      depth: 1,
    }),
    payload.find({
      collection: 'categories',
      depth: 0,
    }),
  ])

  return (
    <div>
      <CategoryNav categories={categoriesResult.docs} />
      <PostList posts={postsResult.docs} />
    </div>
  )
}
```

---

## 🚨 Error Handling

### Always Use Try-Catch

**Rule**: Never let data fetching errors crash the app

```typescript
// ✅ Good: Graceful error handling
export default async function HomePage() {
  try {
    const payload = await getPayload({ config })
    const posts = await payload.find({ collection: 'posts' })

    return <PostList posts={posts.docs} />
  } catch (error) {
    console.error('Failed to fetch posts:', error)

    return (
      <div className="error-fallback">
        <h2>Unable to load posts</h2>
        <p>Please try again later.</p>
      </div>
    )
  }
}
```

### Error Boundaries for Client Components

```typescript
// app/error.tsx (Next.js error boundary)
'use client'

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  return (
    <div>
      <h2>Something went wrong!</h2>
      <button onClick={() => reset()}>Try again</button>
    </div>
  )
}
```

---

## ⏳ Loading States with Suspense

### Suspense Boundaries

**Rule**: Wrap slow data fetching in Suspense for better UX

```typescript
// ✅ Good: Suspense boundary for slow data
import { Suspense } from 'react'

export default function PostsPage() {
  return (
    <div>
      <h1>Latest Posts</h1>
      <Suspense fallback={<PostsSkeleton />}>
        <PostsList />
      </Suspense>
    </div>
  )
}

// This component can take time to load
async function PostsList() {
  const posts = await fetchPosts() // Slow operation
  return (
    <div>
      {posts.map(post => <PostCard key={post.id} post={post} />)}
    </div>
  )
}

function PostsSkeleton() {
  return (
    <div className="skeleton">
      {[...Array(5)].map((_, i) => (
        <div key={i} className="skeleton-card" />
      ))}
    </div>
  )
}
```

### Multiple Suspense Boundaries

**Pattern**: Separate fast and slow data

```typescript
export default function HomePage() {
  return (
    <div>
      {/* Fast: Loads immediately */}
      <Suspense fallback={<HeaderSkeleton />}>
        <Header />
      </Suspense>

      {/* Slow: Loads independently */}
      <Suspense fallback={<PostsSkeleton />}>
        <RecentPosts />
      </Suspense>

      {/* Slow: Loads independently */}
      <Suspense fallback={<SidebarSkeleton />}>
        <Sidebar />
      </Suspense>
    </div>
  )
}
```

---

## 🔍 PayloadCMS Query Optimization

### Use `depth` Parameter

**Rule**: Limit relationship depth to avoid over-fetching

```typescript
// ❌ Bad: Over-fetching (default depth = 2)
const posts = await payload.find({
  collection: 'posts',
  // Fetches posts → author → avatar → ... (deep nesting)
})

// ✅ Good: Limit depth
const posts = await payload.find({
  collection: 'posts',
  depth: 1, // Only populate first level (author, category, heroImage)
})

// ✅ Good: No relationships needed
const categories = await payload.find({
  collection: 'categories',
  depth: 0, // Don't populate any relationships
})
```

### Use `select` for Specific Fields

**Rule**: Only fetch fields you need

```typescript
// ❌ Bad: Fetch all fields
const posts = await payload.find({
  collection: 'posts',
  // Returns all fields including large content
})

// ✅ Good: Only fetch needed fields
const posts = await payload.find({
  collection: 'posts',
  select: {
    title: true,
    slug: true,
    publishedDate: true,
    heroImage: true,
  },
})
```

### Use `where` for Filtering

**Rule**: Filter at database level, not in JavaScript

```typescript
// ❌ Bad: Fetch all then filter in JavaScript
const allPosts = await payload.find({ collection: 'posts' })
const techPosts = allPosts.docs.filter((p) => p.category.slug === 'tech')

// ✅ Good: Filter at database level
const techPosts = await payload.find({
  collection: 'posts',
  where: {
    'category.slug': {
      equals: 'tech',
    },
  },
})
```

### Use `limit` for Pagination

```typescript
// ✅ Good: Paginated query
const posts = await payload.find({
  collection: 'posts',
  limit: 10,
  page: 1,
  sort: '-publishedDate',
})

console.log(posts.docs) // Array of 10 posts
console.log(posts.totalDocs) // Total count
console.log(posts.hasNextPage) // Boolean
```

---

## 🎨 Real-World Patterns

### Homepage with Categories and Posts

```typescript
// src/app/(frontend)/page.tsx
export const dynamic = 'force-dynamic'

export default async function HomePage() {
  try {
    const payload = await getPayload({ config })

    // Parallel fetching for performance
    const [postsResult, categoriesResult] = await Promise.all([
      payload.find({
        collection: 'posts',
        sort: '-publishedDate',
        limit: 10,
        depth: 1, // Populate author, category, heroImage
        select: {
          title: true,
          slug: true,
          heroImage: true,
          author: true,
          category: true,
          publishedDate: true,
        },
      }),
      payload.find({
        collection: 'categories',
        depth: 0, // No relationships needed
      }),
    ])

    return (
      <div>
        <CategoryNav categories={categoriesResult.docs} />
        <PostList posts={postsResult.docs} />
      </div>
    )
  } catch (error) {
    console.error('Failed to fetch homepage data:', error)
    return <ErrorFallback />
  }
}
```

### Category Page with Filtered Posts

```typescript
// src/app/(frontend)/category/[slug]/page.tsx
export const dynamic = 'force-dynamic'

export default async function CategoryPage({
  params,
}: {
  params: { slug: string }
}) {
  try {
    const payload = await getPayload({ config })

    // Parallel: Fetch category and its posts
    const [category, postsResult] = await Promise.all([
      payload.find({
        collection: 'categories',
        where: { slug: { equals: params.slug } },
        limit: 1,
      }),
      payload.find({
        collection: 'posts',
        where: {
          'category.slug': { equals: params.slug },
        },
        sort: '-publishedDate',
        depth: 1,
      }),
    ])

    if (!category.docs[0]) {
      return <div>Category not found</div>
    }

    return (
      <div>
        <CategoryHeader category={category.docs[0]} />
        <PostList posts={postsResult.docs} />
      </div>
    )
  } catch (error) {
    console.error('Failed to fetch category page:', error)
    return <ErrorFallback />
  }
}
```

### Post Detail Page

```typescript
// src/app/(frontend)/posts/[slug]/page.tsx
export const dynamic = 'force-dynamic'

export default async function PostPage({
  params,
}: {
  params: { slug: string }
}) {
  try {
    const payload = await getPayload({ config })

    const result = await payload.find({
      collection: 'posts',
      where: { slug: { equals: params.slug } },
      limit: 1,
      depth: 2, // Populate author with avatar, category with heroImage
    })

    const post = result.docs[0]

    if (!post) {
      return <div>Post not found</div>
    }

    return <PostContent post={post} />
  } catch (error) {
    console.error('Failed to fetch post:', error)
    return <ErrorFallback />
  }
}
```

---

## 🚫 Anti-Patterns

### Don't Fetch in Client Components

```typescript
// ❌ Bad: Fetching in Client Component
'use client'
import { useState, useEffect } from 'react'

export function PostList() {
  const [posts, setPosts] = useState([])

  useEffect(() => {
    fetch('/api/posts')
      .then(res => res.json())
      .then(setPosts)
  }, [])

  return <div>{/* render posts */}</div>
}

// ✅ Good: Fetch in Server Component, pass to Client Component
export default async function PostsPage() {
  const posts = await fetchPosts()
  return <PostListClient posts={posts} />
}

'use client'
export function PostListClient({ posts }) {
  // Client-side interactivity only
  return <div>{/* render posts */}</div>
}
```

### Don't Prop Drill from Root Layout

```typescript
// ❌ Bad: Fetch at root, prop drill everywhere
export default async function RootLayout({ children }) {
  const posts = await fetchPosts()
  return <html><body><App posts={posts}>{children}</App></body></html>
}

// ✅ Good: Fetch close to usage
export default async function HomePage() {
  const posts = await fetchPosts()
  return <PostList posts={posts} />
}
```

---

## 📚 Related Documentation

- [ADR-003: Next.js App Router Architecture](../docs/adr/ADR-003-nextjs-architecture.md)
- [Coding Standards: Data Fetching](../docs/CODING_STANDARDS.md)
- [PayloadCMS Patterns](../skills/payload-cms-patterns/SKILL.md)

## 🔗 References

- [Next.js Data Fetching](https://nextjs.org/docs/app/building-your-application/data-fetching)
- [Server Components](https://nextjs.org/docs/app/building-your-application/rendering/server-components)
- [PayloadCMS Local API](https://payloadcms.com/docs/local-api/overview)
