---
description: Testing strategy and best practices for the News Blog project using Vitest and Playwright.
---

# Testing Strategy

You are working on a News Blog project with a three-tier testing strategy: Unit tests, Integration tests, and E2E tests. Follow these patterns to ensure code quality and prevent regressions.

## 🎯 Testing Philosophy

**Goal**: 80% coverage on critical paths without slowing down development velocity.

**Critical Paths**:

- `src/app/(frontend)/utils.ts` - All utility functions
- `src/collections/*.ts` - PayloadCMS collection operations
- Authentication flows
- Data fetching logic

## 📊 Testing Pyramid

```
        /\
       /E2E\      ← Playwright (Slow, High confidence)
      /------\
     /  INT   \   ← Vitest + PayloadCMS (Medium speed)
    /----------\
   /   UNIT     \ ← Vitest (Fast, Low-level)
  /--------------\
```

## 🧪 Test Types

### Unit Tests (`tests/unit/`)

**Tool**: Vitest  
**Speed**: Milliseconds  
**Purpose**: Test pure utility functions in isolation

**When to write**:

- Data transformation functions
- Validation logic
- Helper utilities
- Any pure function (no side effects)

**Example**:

```typescript
// tests/unit/utils.test.ts
import { describe, it, expect } from 'vitest'
import { getHeroImageUrl, filterPostsByCategory } from '@/app/(frontend)/utils'

describe('getHeroImageUrl', () => {
  it('should return URL when heroImage is populated object', () => {
    // Arrange
    const heroImage = { url: '/media/image.jpg', id: '123' }

    // Act
    const result = getHeroImageUrl(heroImage)

    // Assert
    expect(result).toBe('/media/image.jpg')
  })

  it('should return null when heroImage is undefined', () => {
    expect(getHeroImageUrl(undefined)).toBeNull()
  })

  it('should return null when heroImage is ID string', () => {
    expect(getHeroImageUrl('some-id')).toBeNull()
  })
})
```

### Integration Tests (`tests/int/`)

**Tool**: Vitest with PayloadCMS instance  
**Speed**: Seconds  
**Purpose**: Test PayloadCMS collections and database interactions

**When to write**:

- CRUD operations on collections
- Relationship integrity
- Unique constraints
- Authentication flows
- Hooks and validation

**Example**:

```typescript
// tests/int/collections/posts.test.ts
import { describe, it, expect, beforeAll, afterAll } from 'vitest'
import { getPayload } from 'payload'
import config from '@/payload.config'

describe('Posts Collection', () => {
  let payload

  beforeAll(async () => {
    payload = await getPayload({ config })
  })

  it('should create a post with required fields', async () => {
    // Arrange
    const postData = {
      title: 'Test Post',
      slug: 'test-post',
      content: { root: { children: [] } },
      author: authorId,
      category: categoryId,
      heroImage: mediaId,
    }

    // Act
    const post = await payload.create({
      collection: 'posts',
      data: postData,
    })

    // Assert
    expect(post.title).toBe('Test Post')
    expect(post.slug).toBe('test-post')
  })

  it('should enforce unique slug constraint', async () => {
    // Arrange
    await payload.create({
      collection: 'posts',
      data: { title: 'First', slug: 'duplicate-slug' /* ... */ },
    })

    // Act & Assert
    await expect(
      payload.create({
        collection: 'posts',
        data: { title: 'Second', slug: 'duplicate-slug' /* ... */ },
      }),
    ).rejects.toThrow()
  })
})
```

### E2E Tests (`tests/e2e/`)

**Tool**: Playwright  
**Speed**: Seconds to minutes  
**Purpose**: Test complete user flows in real browser

**When to write**:

- Homepage loads and displays posts
- Navigation between pages
- Category filtering
- Post detail pages
- Search functionality

**Example**:

```typescript
// tests/e2e/homepage.spec.ts
import { test, expect } from '@playwright/test'

test('homepage displays recent posts', async ({ page }) => {
  // Arrange & Act
  await page.goto('http://localhost:3000')

  // Assert
  await expect(page.getByRole('banner')).toBeVisible()

  const posts = page.locator('[data-testid="post-card"]')
  await expect(posts).toHaveCount(10)
})

test('clicking post navigates to detail page', async ({ page }) => {
  // Arrange
  await page.goto('http://localhost:3000')

  // Act
  await page.locator('[data-testid="post-card"]').first().click()

  // Assert
  await expect(page).toHaveURL(/\/posts\//)
  await expect(page.locator('article')).toBeVisible()
})
```

## 📐 AAA Pattern (Arrange-Act-Assert)

**Rule**: All tests MUST follow the AAA pattern for readability.

```typescript
it('should filter posts by category', () => {
  // Arrange: Set up test data
  const posts = [
    { id: '1', category: { id: 'tech' } },
    { id: '2', category: { id: 'startup' } },
    { id: '3', category: { id: 'tech' } },
  ]
  const categoryId = 'tech'

  // Act: Call the function
  const result = filterPostsByCategory(posts, categoryId)

  // Assert: Verify outcome
  expect(result).toHaveLength(2)
  expect(result[0].id).toBe('1')
  expect(result[1].id).toBe('3')
})
```

## 🎯 Test Naming Convention

**Format**: `should [expected behavior] when [condition]`

```typescript
// ✅ Good: Descriptive and clear
it('should return null when heroImage is undefined', () => {})
it('should filter posts by category when categoryId is provided', () => {})
it('should return all posts when categoryId is null', () => {})
it('should throw error when required field is missing', () => {})

// ❌ Bad: Vague and unclear
it('test heroImage', () => {})
it('works', () => {})
it('filters correctly', () => {})
```

## 😢 Test Sad Paths

**Rule**: Don't just test when things go right. Test error cases too.

```typescript
describe('getHeroImageUrl', () => {
  // Happy path
  it('should return URL when heroImage is populated object', () => {
    const heroImage = { url: '/media/image.jpg', id: '123' }
    expect(getHeroImageUrl(heroImage)).toBe('/media/image.jpg')
  })

  // Sad paths
  it('should return null when heroImage is undefined', () => {
    expect(getHeroImageUrl(undefined)).toBeNull()
  })

  it('should return null when heroImage is null', () => {
    expect(getHeroImageUrl(null)).toBeNull()
  })

  it('should return null when heroImage is ID string', () => {
    expect(getHeroImageUrl('some-id')).toBeNull()
  })

  it('should return null when heroImage object has no url property', () => {
    expect(getHeroImageUrl({ id: '123' })).toBeNull()
  })
})
```

## 🚀 Running Tests

### Development Workflow

```bash
# Watch mode (recommended during development)
npx vitest

# Run all unit and integration tests
npm run test:int

# Run E2E tests (requires dev server running)
npm run test:e2e

# Run coverage report
npm run test:coverage
```

### Pre-Commit

Tests run automatically via Husky pre-commit hooks:

- ESLint checks
- TypeScript type checking
- Unit tests (fast)

## 📊 Coverage Requirements

### Critical Paths (80% coverage)

**Files**:

- `src/app/(frontend)/utils.ts`
- `src/collections/*.ts`

**Run**:

```bash
npm run test:coverage:critical
```

**Configuration**:

```typescript
// vitest.config.mts
coverage: {
  include: [
    'src/app/(frontend)/utils.ts',
    'src/collections/**/*.ts',
  ],
  thresholds: {
    lines: 80,
    functions: 80,
    branches: 80,
    statements: 80,
  },
}
```

### Nice to Have (60% coverage)

- UI components
- Static pages
- Admin customizations

## 🧩 Pure Logic Rule

**Rule**: Extract complex logic to utility functions for easy testing.

```typescript
// ✅ Good: Pure function in utils.ts (easy to test)
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
  const imageUrl = getHeroImageUrl(post.heroImage)
  return <img src={imageUrl} alt={post.title} />
}

// ❌ Bad: Logic in component (hard to test)
export default async function PostPage({ params }) {
  const post = await fetchPost(params.slug)
  const imageUrl = typeof post.heroImage === 'object' ? post.heroImage.url : null
  return <img src={imageUrl} alt={post.title} />
}
```

## 🔄 Test Isolation

**Rule**: Each test must be independent and can run in any order.

```typescript
// ✅ Good: Independent tests
describe('filterPostsByCategory', () => {
  it('should filter posts by category', () => {
    const posts = [
      /* fresh data */
    ]
    const result = filterPostsByCategory(posts, 'tech')
    expect(result).toHaveLength(2)
  })

  it('should return all posts when categoryId is null', () => {
    const posts = [
      /* fresh data */
    ]
    const result = filterPostsByCategory(posts, null)
    expect(result).toHaveLength(3)
  })
})

// ❌ Bad: Tests depend on shared state
let posts = []

it('should add post', () => {
  posts.push({ id: '1' })
  expect(posts).toHaveLength(1)
})

it('should filter posts', () => {
  // Depends on previous test running first!
  const result = filterPostsByCategory(posts, 'tech')
  expect(result).toHaveLength(1)
})
```

## ⚡ Test Performance

**Rule**: Keep unit tests under 100ms each.

```typescript
// ✅ Good: Fast unit test
it('should return URL when heroImage is populated object', () => {
  const heroImage = { url: '/media/image.jpg', id: '123' }
  expect(getHeroImageUrl(heroImage)).toBe('/media/image.jpg')
  // Runs in < 1ms
})

// ⚠️ Acceptable: Integration test (slower)
it('should create a post', async () => {
  const post = await payload.create({
    /* ... */
  })
  expect(post.title).toBe('Test')
  // Runs in ~100-500ms (database operation)
})
```

## 🎨 Test Data Patterns

### Minimal Test Data

**Rule**: Use minimal data needed for the test.

```typescript
// ✅ Good: Only necessary fields
it('should filter posts by category', () => {
  const posts = [
    { id: '1', category: { id: 'tech' } },
    { id: '2', category: { id: 'startup' } },
  ]
  const result = filterPostsByCategory(posts, 'tech')
  expect(result).toHaveLength(1)
})

// ❌ Bad: Unnecessary data
it('should filter posts by category', () => {
  const posts = [
    {
      id: '1',
      title: 'Test Post',
      slug: 'test-post',
      content: 'Long content...',
      author: { id: 'author-1', name: 'John' },
      category: { id: 'tech', name: 'Technology' },
      publishedDate: '2026-01-01',
    },
    // ... more unnecessary data
  ]
  const result = filterPostsByCategory(posts, 'tech')
  expect(result).toHaveLength(1)
})
```

## 🐛 Debugging Tests

### Use `it.only` for Focused Testing

```typescript
// Run only this test
it.only('should filter posts by category', () => {
  // ... test code
})
```

### Use `it.skip` to Temporarily Disable

```typescript
// Skip this test
it.skip('should handle edge case', () => {
  // ... test code
})
```

### Use `console.log` for Debugging

```typescript
it('should filter posts', () => {
  const posts = [
    /* ... */
  ]
  const result = filterPostsByCategory(posts, 'tech')

  console.log('Input:', posts)
  console.log('Output:', result)

  expect(result).toHaveLength(2)
})
```

## 📚 Related Documentation

- [ADR-004: Testing Strategy](../docs/adr/ADR-004-testing-strategy.md)
- [Coding Standards: Pure Logic Rule](../docs/CODING_STANDARDS.md)
- [TESTING.md](../../TESTING.md)

## 🔗 References

- [Vitest Documentation](https://vitest.dev/)
- [Playwright Documentation](https://playwright.dev/)
- [Testing Library Best Practices](https://testing-library.com/docs/guiding-principles)
