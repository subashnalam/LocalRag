# Coding Standards

This document defines the coding standards for the News Blog project. Following these standards ensures consistency, maintainability, and prevents breaking changes.

## 🎯 Core Principles

1. **Server Components First**: Default to Server Components; add `'use client'` only when necessary
2. **Pure Logic Extraction**: Extract complex logic to utility functions for testability
3. **Type Safety**: Use TypeScript strictly; avoid `any` types
4. **Error Handling**: Always handle errors gracefully; never crash the app
5. **Performance**: Optimize for Core Web Vitals (LCP, CLS, FID)

---

## 🏗️ Architecture Patterns

### Server Components vs Client Components

**Default**: All components are Server Components

**When to use Client Components** (add `'use client'`):

- State management (`useState`, `useReducer`, `useContext`)
- Effects (`useEffect`, `useLayoutEffect`)
- Event handlers (`onClick`, `onChange`, `onSubmit`)
- Browser APIs (`localStorage`, `window`, `document`)
- Third-party libraries that require client-side rendering

**Example**:

```typescript
// ✅ Good: Server Component (default)
export default async function PostPage({ params }: { params: { slug: string } }) {
  const payload = await getPayload({ config })
  const post = await payload.findByID({ collection: 'posts', id: params.slug })
  return <PostContent post={post} />
}

// ✅ Good: Client Component (when needed)
'use client'
import { useState } from 'react'

export function SearchBar() {
  const [query, setQuery] = useState('')
  return <input value={query} onChange={(e) => setQuery(e.target.value)} />
}
```

---

## 📊 Data Fetching

### Parallel Fetching

**Rule**: Use `Promise.all` for independent asynchronous operations

```typescript
// ❌ Bad: Sequential waterfall (slow)
const posts = await payload.find({ collection: 'posts' })
const categories = await payload.find({ collection: 'categories' })

// ✅ Good: Parallel fetching (fast)
const [posts, categories] = await Promise.all([
  payload.find({ collection: 'posts' }),
  payload.find({ collection: 'categories' }),
])
```

### Fetch Close to Usage

**Rule**: Fetch data in the component that needs it, not at the root layout

**Reason**: Next.js deduplicates `fetch` requests automatically

```typescript
// ✅ Good: Fetch in page component
export default async function HomePage() {
  const posts = await fetchPosts() // Fetched here
  return <PostList posts={posts} />
}

// ❌ Bad: Prop drilling from root layout
export default function RootLayout() {
  const posts = await fetchPosts() // Too high up
  return <HomePage posts={posts} /> // Prop drilling
}
```

### Error Handling

**Rule**: Always handle errors gracefully with try-catch

```typescript
// ✅ Good: Graceful error handling
export default async function HomePage() {
  try {
    const payload = await getPayload({ config })
    const posts = await payload.find({ collection: 'posts' })
    return <PostList posts={posts.docs} />
  } catch (error) {
    console.error('Failed to fetch posts:', error)
    return <ErrorFallback message="Unable to load posts. Please try again later." />
  }
}
```

---

## 🧪 Testing & Testability

### Pure Logic Rule

**Rule**: Extract complex logic to utility functions in `utils.ts`

**Why**: Pure functions are easy to test without mocking

```typescript
// ✅ Good: Extract to utils.ts
// utils.ts
export function getHeroImageUrl(heroImage: Post['heroImage']): string | null {
  if (typeof heroImage === 'object' && heroImage !== null && 'url' in heroImage) {
    return heroImage.url || null
  }
  return null
}

// page.tsx
import { getHeroImageUrl } from './utils'

export default async function PostPage({ params }) {
  const post = await fetchPost(params.slug)
  const imageUrl = getHeroImageUrl(post.heroImage) // Easy to test
  return <img src={imageUrl} alt={post.title} />
}

// ❌ Bad: Logic in component (hard to test)
export default async function PostPage({ params }) {
  const post = await fetchPost(params.slug)
  const imageUrl = typeof post.heroImage === 'object' ? post.heroImage.url : null
  return <img src={imageUrl} alt={post.title} />
}
```

### AAA Pattern

**Rule**: All tests follow Arrange-Act-Assert pattern

```typescript
it('should filter posts by category', () => {
  // Arrange: Set up test data
  const posts = [{ id: '1', category: { id: 'tech' } }]
  const categoryId = 'tech'

  // Act: Call the function
  const result = filterPostsByCategory(posts, categoryId)

  // Assert: Verify outcome
  expect(result).toHaveLength(1)
})
```

---

## 📝 TypeScript

### Interfaces for Props

**Rule**: Use `interface` for component props, `type` for unions/intersections

```typescript
// ✅ Good: Interface for props
interface PostCardProps {
  title: string
  slug: string
  heroImage: string | null
}

export function PostCard({ title, slug, heroImage }: PostCardProps) {
  return <div>{title}</div>
}

// ✅ Good: Type for unions
type Status = 'draft' | 'published' | 'archived'
```

### Avoid `any`

**Rule**: Never use `any` type; use `unknown` if type is truly unknown

```typescript
// ❌ Bad: Using any
function processData(data: any) {
  return data.value
}

// ✅ Good: Use proper types
function processData(data: Post) {
  return data.title
}

// ✅ Good: Use unknown for truly unknown types
function processData(data: unknown) {
  if (typeof data === 'object' && data !== null && 'value' in data) {
    return data.value
  }
  return null
}
```

### Use Generated Types

**Rule**: Always use auto-generated types from `payload-types.ts`

```typescript
// ✅ Good: Use generated types
import type { Post, Category } from '@/payload-types'

function renderPost(post: Post) {
  return <div>{post.title}</div>
}

// ❌ Bad: Manual types (will drift from schema)
interface Post {
  title: string
  slug: string
}
```

---

## 🎨 Naming Conventions

### Files and Components

- **Components**: PascalCase (`PostCard.tsx`, `Header.tsx`)
- **Utilities**: camelCase (`utils.ts`, `formatDate.ts`)
- **Pages**: lowercase (`page.tsx`, `layout.tsx`)
- **Tests**: Match source file with `.test.ts` suffix (`utils.test.ts`)

### Functions and Variables

- **Components**: PascalCase (`function PostCard() {}`)
- **Functions**: camelCase (`function fetchPosts() {}`)
- **Constants**: UPPER_SNAKE_CASE (`const MAX_POSTS = 10`)
- **Variables**: camelCase (`const postCount = 5`)

### Test Names

**Format**: `should [expected behavior] when [condition]`

```typescript
// ✅ Good
it('should return null when heroImage is undefined', () => {})
it('should filter posts by category when categoryId is provided', () => {})

// ❌ Bad
it('test heroImage', () => {})
it('works', () => {})
```

---

## 🖼️ Images and Media

### Always Use `next/image`

**Rule**: Never use raw `<img>` tags; always use `next/image`

```typescript
// ✅ Good: Using next/image
import Image from 'next/image'

export function PostCard({ heroImage, title }: PostCardProps) {
  return (
    <Image
      src={heroImage}
      alt={title}
      width={800}
      height={600}
      sizes="(max-width: 768px) 100vw, 800px"
    />
  )
}

// ❌ Bad: Raw img tag
export function PostCard({ heroImage, title }: PostCardProps) {
  return <img src={heroImage} alt={title} />
}
```

---

## 🗂️ File Organization

### Colocation

**Rule**: Keep related files close together

```
(frontend)/
├── components/
│   ├── Header.tsx
│   ├── Footer.tsx
│   └── PostCard.tsx
├── posts/
│   └── [slug]/
│       └── page.tsx
├── utils.ts
└── styles.css
```

### Utility Functions

**Rule**: Group utilities by feature, not by type

```
// ✅ Good: Feature-based
utils.ts              # Frontend utilities
collections/
  Posts.ts            # Post-specific logic

// ❌ Bad: Type-based
utils/
  strings.ts
  dates.ts
  images.ts
```

---

## 🚨 Error Handling

### Never Crash the App

**Rule**: Always provide fallback UI for errors

```typescript
// ✅ Good: Error boundary with fallback
export default async function HomePage() {
  try {
    const posts = await fetchPosts()
    return <PostList posts={posts} />
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

### Validate User Input

**Rule**: Validate all user input before processing

```typescript
// ✅ Good: Input validation
export function filterPostsByCategory(posts: Post[], categoryId: string | null): Post[] {
  if (!categoryId) return posts // Handle null case
  if (!Array.isArray(posts)) return [] // Validate input

  return posts.filter((post) => {
    if (!post.category) return false
    // ... filtering logic
  })
}
```

---

## ⚡ Performance

### Bundle Size

**Rule**: Use dynamic imports for heavy components

```typescript
// ✅ Good: Dynamic import for heavy component
import dynamic from 'next/dynamic'

const HeavyChart = dynamic(() => import('./HeavyChart'), {
  loading: () => <p>Loading chart...</p>,
})

// ❌ Bad: Static import for heavy component
import HeavyChart from './HeavyChart'
```

### Loading States

**Rule**: Use Suspense boundaries for slow data fetching

```typescript
// ✅ Good: Suspense boundary
import { Suspense } from 'react'

export default function PostsPage() {
  return (
    <Suspense fallback={<PostsSkeleton />}>
      <PostsList />
    </Suspense>
  )
}

async function PostsList() {
  const posts = await fetchPosts() // Slow operation
  return <div>{/* render posts */}</div>
}
```

---

## 📦 Exports

### Named Exports

**Rule**: Prefer named exports over default exports

```typescript
// ✅ Good: Named export
export function PostCard({ title }: PostCardProps) {
  return <div>{title}</div>
}

// ❌ Bad: Default export (harder to refactor)
export default function PostCard({ title }: PostCardProps) {
  return <div>{title}</div>
}

// Exception: Page components must use default export
export default function HomePage() {
  return <div>Home</div>
}
```

---

## 🔒 Security

### Environment Variables

**Rule**: Never commit secrets; use `.env` files

```typescript
// ✅ Good: Use environment variables
const secret = process.env.PAYLOAD_SECRET

// ❌ Bad: Hardcoded secrets
const secret = 'my-secret-key-123'
```

### Input Sanitization

**Rule**: Sanitize user input before rendering

```typescript
// ✅ Good: React automatically escapes
<div>{userInput}</div>

// ⚠️ Dangerous: Only use when necessary
<div dangerouslySetInnerHTML={{ __html: sanitizedHTML }} />
```

---

## 📚 Documentation

### Code Comments

**Rule**: Comment "why", not "what"

```typescript
// ✅ Good: Explains why
// PayloadCMS can return category as object or ID depending on depth
if (typeof post.category === 'object' && 'id' in post.category) {
  return post.category.id
}

// ❌ Bad: Explains what (obvious from code)
// Check if category is object
if (typeof post.category === 'object') {
  return post.category.id
}
```

### Function Documentation

**Rule**: Document complex functions with JSDoc

```typescript
/**
 * Safely extracts image URL from post's heroImage field
 * Handles both populated Media objects and ID references
 *
 * @param heroImage - Post's heroImage field (can be Media object or ID)
 * @returns Image URL or null if not available
 */
export function getHeroImageUrl(heroImage: Post['heroImage']): string | null {
  // ...
}
```

---

## 🔄 Git Workflow

### Commit Messages

**Format**: `type(scope): description`

**Types**: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

```bash
# ✅ Good
feat(posts): add category filtering
fix(header): resolve mobile menu overflow
docs(readme): update installation steps

# ❌ Bad
updated stuff
fix bug
WIP
```

### Pre-Commit Checks

**Automatic** (via Husky):

- ESLint (max 10 warnings)
- Prettier formatting
- TypeScript type checking

---

## 📖 Related Documentation

- [ADR-001: PayloadCMS](./adr/ADR-001-payloadcms.md)
- [ADR-002: SQLite](./adr/ADR-002-sqlite.md)
- [ADR-003: Next.js Architecture](./adr/ADR-003-nextjs-architecture.md)
- [ADR-004: Testing Strategy](./adr/ADR-004-testing-strategy.md)
- [TESTING.md](../../TESTING.md)
