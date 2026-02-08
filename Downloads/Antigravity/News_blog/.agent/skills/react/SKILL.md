---
description: Expert guidelines for React and Next.js development, focused on performance and Vercel best practices.
---

# React & Next.js Best Practices

You are an expert React/Next.js developer following Vercel's engineering standards. Apply these rules to all React code.

## 🚨 CRITICAL: Performance Killers

### 1. Eliminate Waterfalls
**Rule:** Never await independent asynchronous operations sequentially.
**Fix:** Use `Promise.all` to initiate requests in parallel.

```typescript
// ❌ Bad: Waterfall
const user = await getUser(id);
const posts = await getPosts(id); // Waits for user

// ✅ Good: Parallel
const [user, posts] = await Promise.all([
  getUser(id),
  getPosts(id)
]);
```

### 2. Bundle Size Optimization
**Rule:** Import specific modules to facilitate tree-shaking. Avoid barrel files for libraries.
**Fix:**
- Use `import { x } from 'package/x'` logic where possible or configured.
- Use `next/dynamic` for heavy components (charts, maps) that are not critical for LCP.

```typescript
// ❌ Bad
import { HeavyComponent } from './components'

// ✅ Good
import dynamic from 'next/dynamic'
const HeavyComponent = dynamic(() => import('./components/HeavyComponent'))
```

## ⚡ HIGH: Server & Architecture

### 3. Server Components First
**Rule:** All components are Server Components by default. Only add `'use client'` when strictly necessary (state, effects, event listeners).
**Fix:** Move purely presentational logic or data fetching to Server Components. Pass specific interactive parts as slots or independent Client Components.

### 4. Efficient Data Fetching
**Rule:** Fetch data close to where it is used.
**Fix:** Don't prop-drill data from Root Layouts. Next.js extends `fetch` to dedup requests, so call it in the component that needs it.

## 🛠️ MEDIUM: Rendering & UX

### 5. Suspense Boundaries
**Rule:** Don't block the entire page for one slow data source.
**Fix:** Wrap slow parts in `<Suspense fallback={<Skeleton />}>` so the "App Shell" loads instantly.

### 6. Image Optimization
**Rule:** Never use raw `<img>` tags.
**Fix:** Always use `next/image` with `width`, `height`, and `alt`. Use `sizes` prop for responsive images.

## 📝 Code Style & Conventions

- **Naming**: PascalCase for components (`UserProfile.tsx`), camelCase for helpers.
- **Props**: Use `interface` over `type` for component props.
- **Exports**: Use named exports (`export function Component()`) to avoid "default export" refactoring pain.
