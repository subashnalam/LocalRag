# TypeScript Strict Mode Migration Guide

**Current Status**: Strict mode is **disabled**  
**Target**: Enable full strict mode for better type safety

## 🎯 Why Strict Mode?

### Benefits

✅ **Catch Null/Undefined Errors**: Prevent `Cannot read property 'x' of undefined` at compile time  
✅ **Better IDE Support**: Improved autocomplete and error detection  
✅ **Prevent Implicit Any**: No more accidental `any` types  
✅ **Safer Refactoring**: TypeScript catches more breaking changes  
✅ **Production Quality**: Industry best practice for TypeScript projects

### Trade-offs

⚠️ **Initial Work**: Need to fix existing type errors  
⚠️ **Stricter Rules**: More explicit type annotations required  
⚠️ **Learning Curve**: Team needs to understand strict mode patterns

---

## 📊 Current Configuration

```json
// tsconfig.json (current)
{
  "compilerOptions": {
    "strict": false // Currently disabled
    // ...
  }
}
```

---

## 🚀 Migration Strategy

### Phase 1: Enable `noImplicitAny`

**What it does**: Prevents implicit `any` types

**Step 1**: Update `tsconfig.json`

```json
{
  "compilerOptions": {
    "noImplicitAny": true
    // ...
  }
}
```

**Step 2**: Find errors

```bash
npx tsc --noEmit
```

**Step 3**: Fix errors

```typescript
// ❌ Before: Implicit any
function processData(data) {
  return data.value
}

// ✅ After: Explicit type
function processData(data: { value: string }) {
  return data.value
}
```

---

### Phase 2: Enable `strictNullChecks`

**What it does**: `null` and `undefined` are not assignable to other types

**Step 1**: Update `tsconfig.json`

```json
{
  "compilerOptions": {
    "noImplicitAny": true,
    "strictNullChecks": true
    // ...
  }
}
```

**Step 2**: Fix errors

```typescript
// ❌ Before: Potential null error
function getHeroImageUrl(heroImage: Post['heroImage']): string {
  return heroImage.url // Error: heroImage might be null
}

// ✅ After: Handle null case
function getHeroImageUrl(heroImage: Post['heroImage']): string | null {
  if (typeof heroImage === 'object' && heroImage !== null && 'url' in heroImage) {
    return heroImage.url || null
  }
  return null
}
```

---

### Phase 3: Enable Full `strict` Mode

**What it does**: Enables all strict type checking options

**Step 1**: Update `tsconfig.json`

```json
{
  "compilerOptions": {
    "strict": true
    // ...
  }
}
```

**Step 2**: Fix remaining errors

```bash
npx tsc --noEmit
```

---

## 🛠️ Common Patterns

### Handling Null/Undefined

```typescript
// ✅ Good: Optional chaining
const url = post.heroImage?.url ?? '/default.jpg'

// ✅ Good: Type guard
if (post.heroImage && typeof post.heroImage === 'object') {
  const url = post.heroImage.url
}

// ✅ Good: Non-null assertion (when you're sure)
const url = post.heroImage!.url // Use sparingly!
```

### Function Parameters

```typescript
// ✅ Good: Explicit types
function createPost(title: string, slug: string): Post {
  return { title, slug }
}

// ✅ Good: Optional parameters
function createPost(title: string, slug?: string): Post {
  return { title, slug: slug ?? slugify(title) }
}
```

### Array Methods

```typescript
// ✅ Good: Type-safe filter
const posts: Post[] = allPosts.filter((post): post is Post => {
  return post.category !== null
})

// ✅ Good: Type-safe map
const titles: string[] = posts.map((post) => post.title)
```

---

## 📁 Files to Update (Priority Order)

### High Priority (Core Logic)

1. **`src/collections/*.ts`** - PayloadCMS collection schemas
   - Add explicit types for hooks
   - Handle null cases in validation

2. **`src/app/(frontend)/utils.ts`** - Utility functions
   - Already mostly strict-mode compatible
   - May need minor null handling improvements

3. **`src/payload.config.ts`** - Main configuration
   - Verify all config options are typed

### Medium Priority (Pages)

4. **`src/app/(frontend)/page.tsx`** - Homepage
   - Add explicit types for params
   - Handle null cases in data fetching

5. **`src/app/(frontend)/posts/[slug]/page.tsx`** - Post detail page
6. **`src/app/(frontend)/category/[slug]/page.tsx`** - Category page

### Low Priority (Components)

7. **`src/app/(frontend)/components/*.tsx`** - UI components
   - Add prop interfaces
   - Handle null/undefined props

---

## 🧪 Testing During Migration

### Run Type Check

```bash
# Check for type errors without building
npx tsc --noEmit
```

### Run Tests

```bash
# Ensure tests still pass
npm run test:int
```

### Incremental Approach

**Recommended**: Enable strict mode per-file using `// @ts-check` comments

```typescript
// @ts-check
// This file uses strict type checking

export function myFunction(data: string): string {
  return data.toUpperCase()
}
```

---

## 📊 Progress Tracking

### Checklist

- [ ] Phase 1: Enable `noImplicitAny`
  - [ ] Fix `src/collections/*.ts`
  - [ ] Fix `src/app/(frontend)/utils.ts`
  - [ ] Fix `src/payload.config.ts`
  - [ ] Run tests

- [ ] Phase 2: Enable `strictNullChecks`
  - [ ] Fix `src/collections/*.ts`
  - [ ] Fix `src/app/(frontend)/utils.ts`
  - [ ] Fix page components
  - [ ] Run tests

- [ ] Phase 3: Enable full `strict` mode
  - [ ] Fix remaining errors
  - [ ] Run full test suite
  - [ ] Update documentation

---

## 🚦 When to Migrate

**Recommended Timeline**:

1. **Now**: Document the migration path (this file)
2. **After Phase 1 Complete**: When all documentation and skills are in place
3. **Before Production**: Enable strict mode before deploying to production

**Triggers to Start**:

- ✅ All Phase 1 guardrails are working
- ✅ Test coverage reaches 80% on critical paths
- ✅ Team is comfortable with current TypeScript patterns

---

## 🔗 Resources

- [TypeScript Strict Mode](https://www.typescriptlang.org/tsconfig#strict)
- [Migrating to Strict Mode](https://www.typescriptlang.org/docs/handbook/migrating-from-javascript.html)
- [Strict Mode Best Practices](https://www.typescriptlang.org/docs/handbook/2/narrowing.html)

---

## 📝 Notes

**Current Decision**: Strict mode is **deferred** to maintain development velocity during Phase 1.

**Rationale**:

- Focus on establishing guardrails first (pre-commit hooks, testing, documentation)
- Enable strict mode when the system is stable
- Avoid overwhelming the team with too many changes at once

**Next Steps**:

- Complete Phase 1 guardrails
- Reach 80% test coverage on critical paths
- Then enable strict mode incrementally
