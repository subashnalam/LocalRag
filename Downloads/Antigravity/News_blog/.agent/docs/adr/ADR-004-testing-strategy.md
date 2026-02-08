# ADR-004: Testing Strategy

**Status**: Accepted  
**Date**: 2026-02-08  
**Decision Makers**: Development Team

## Context

We needed a comprehensive testing strategy that:

- Ensures code quality and prevents regressions
- Supports rapid development without slowing down velocity
- Covers critical paths thoroughly (80% coverage target)
- Provides fast feedback during development
- Works well with PayloadCMS and Next.js architecture

### Alternatives Considered

1. **Jest + React Testing Library**
   - ✅ Industry standard
   - ❌ Slower than Vitest
   - ❌ More configuration needed

2. **Only E2E Tests (Playwright)**
   - ✅ Tests real user flows
   - ❌ Slow feedback loop
   - ❌ Hard to debug failures
   - ❌ Doesn't test utility functions

3. **No Formal Testing**
   - ✅ Fastest development initially
   - ❌ High risk of regressions
   - ❌ Hard to refactor confidently
   - ❌ Unacceptable for production

## Decision

We adopted a **three-tier testing strategy** using Vitest and Playwright.

### Testing Pyramid

```
        /\
       /E2E\      ← Playwright (User flows)
      /------\
     /  INT   \   ← Vitest (PayloadCMS integration)
    /----------\
   /   UNIT     \ ← Vitest (Pure functions)
  /--------------\
```

### Test Types and Tools

#### 1. Unit Tests (`tests/unit/`)

**Tool**: Vitest  
**Speed**: Milliseconds  
**Purpose**: Test pure utility functions in isolation

**What to Test**:

- Data transformation functions
- Validation logic
- Helper utilities
- Pure business logic

**Example**:

```typescript
// tests/unit/utils.test.ts
import { describe, it, expect } from 'vitest'
import { getHeroImageUrl, filterPostsByCategory } from '@/app/(frontend)/utils'

describe('getHeroImageUrl', () => {
  it('should return URL when heroImage is populated object', () => {
    const heroImage = { url: '/media/image.jpg', id: '123' }
    expect(getHeroImageUrl(heroImage)).toBe('/media/image.jpg')
  })

  it('should return null when heroImage is undefined', () => {
    expect(getHeroImageUrl(undefined)).toBeNull()
  })
})
```

#### 2. Integration Tests (`tests/int/`)

**Tool**: Vitest with PayloadCMS instance  
**Speed**: Seconds  
**Purpose**: Test PayloadCMS collections and database interactions

**What to Test**:

- CRUD operations on collections
- Relationship integrity
- Unique constraints
- Authentication flows
- Hooks and validation

**Example**:

```typescript
// tests/int/collections/posts.test.ts
import { describe, it, expect, beforeAll } from 'vitest'
import { getPayload } from 'payload'
import config from '@/payload.config'

describe('Posts Collection', () => {
  let payload

  beforeAll(async () => {
    payload = await getPayload({ config })
  })

  it('should create a post with required fields', async () => {
    const post = await payload.create({
      collection: 'posts',
      data: {
        title: 'Test Post',
        slug: 'test-post',
        content: 'Content',
        author: authorId,
        category: categoryId,
        heroImage: mediaId,
      },
    })

    expect(post.title).toBe('Test Post')
    expect(post.slug).toBe('test-post')
  })
})
```

#### 3. E2E Tests (`tests/e2e/`)

**Tool**: Playwright  
**Speed**: Seconds to minutes  
**Purpose**: Test complete user flows in real browser

**What to Test**:

- Homepage loads and displays posts
- Navigation between pages
- Category filtering
- Post detail pages
- Search functionality (when added)

**Example**:

```typescript
// tests/e2e/homepage.spec.ts
import { test, expect } from '@playwright/test'

test('homepage displays recent posts', async ({ page }) => {
  await page.goto('http://localhost:3000')

  // Check header is visible
  await expect(page.getByRole('banner')).toBeVisible()

  // Check posts are displayed
  const posts = page.locator('[data-testid="post-card"]')
  await expect(posts).toHaveCount(10)
})
```

### AAA Pattern (Arrange-Act-Assert)

**Rule**: All tests must follow the AAA pattern for readability

```typescript
it('should filter posts by category', () => {
  // Arrange: Set up test data
  const posts = [
    { id: '1', category: { id: 'tech' } },
    { id: '2', category: { id: 'startup' } },
  ]
  const categoryId = 'tech'

  // Act: Call the function
  const result = filterPostsByCategory(posts, categoryId)

  // Assert: Verify outcome
  expect(result).toHaveLength(1)
  expect(result[0].id).toBe('1')
})
```

### Coverage Requirements

**Critical Paths** (80% coverage required):

- `src/app/(frontend)/utils.ts` - All utility functions
- `src/collections/*.ts` - PayloadCMS collection schemas
- Authentication flows
- Data fetching logic

**Nice to Have** (60% coverage):

- UI components
- Static pages
- Admin customizations

**Coverage Reporting**:

```bash
# Run coverage for critical paths
npm run test:coverage:critical

# View HTML report
open coverage/index.html
```

## Consequences

### Positive

✅ **Fast Feedback**: Unit tests run in milliseconds  
✅ **Confidence**: 80% coverage on critical paths  
✅ **Refactoring Safety**: Tests catch breaking changes  
✅ **Documentation**: Tests serve as usage examples  
✅ **Quality**: Prevents regressions  
✅ **Developer Experience**: Vitest watch mode for rapid iteration

### Negative

⚠️ **Initial Time Investment**: Writing tests takes time upfront  
⚠️ **Maintenance**: Tests need updates when code changes  
⚠️ **Learning Curve**: Team needs to learn testing best practices

### Best Practices Established

1. **Pure Logic Rule**: Extract complex logic to utility functions for easy testing
2. **AAA Pattern**: All tests follow Arrange-Act-Assert structure
3. **Test Sad Paths**: Test error cases, not just happy paths
4. **Descriptive Names**: Test names describe expected behavior
5. **Isolated Tests**: Each test is independent and can run in any order
6. **Fast Tests**: Keep unit tests under 100ms each

### Test Naming Convention

**Format**: `should [expected behavior] when [condition]`

**Examples**:

- ✅ `should return null when heroImage is undefined`
- ✅ `should filter posts by category when categoryId is provided`
- ✅ `should throw error when required field is missing`
- ❌ `test heroImage` (too vague)
- ❌ `it works` (not descriptive)

### When to Write Tests

**Before Coding** (TDD):

- Complex algorithms
- Critical business logic
- Bug fixes (write failing test first)

**After Coding**:

- Simple utility functions
- UI components
- Exploratory features

**Always**:

- Before merging to main branch
- When fixing bugs
- When refactoring

## Testing Workflow

### Local Development

1. **Watch Mode**: Run `npx vitest` during development
2. **Pre-Commit**: Tests run automatically via Husky hooks
3. **Coverage Check**: Run `npm run test:coverage:critical` before PR

### Continuous Integration (Future)

1. Run all tests on every PR
2. Block merge if tests fail
3. Generate coverage reports
4. Comment coverage diff on PR

## Related Decisions

- [ADR-003: Next.js App Router Architecture](./ADR-003-nextjs-architecture.md)
- [Coding Standards: Pure Logic Rule](../CODING_STANDARDS.md)

## References

- [Vitest Documentation](https://vitest.dev/)
- [Playwright Documentation](https://playwright.dev/)
- [Testing Library Best Practices](https://testing-library.com/docs/guiding-principles)
- [TESTING.md](../../../TESTING.md)
