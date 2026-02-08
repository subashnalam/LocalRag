# 🧪 Testing Guide

This guide outlines the testing strategy for this News Blog project. Following these practices ensures that your code remains robust and bug-free as you add new features.

## 🚀 How to Run Tests

The project uses **Vitest** for unit/integration tests and **Playwright** for end-to-end (E2E) tests.

### 1. Run All Tests

```bash
npm run test:int
```

_Note: This runs both the integration tests (`tests/int`) and the unit tests (`tests/unit`)._

### 2. Run in Watch Mode (Recommended for Dev)

```bash
npx vitest
```

_This will automatically re-run tests every time you save a file._

### 3. Run E2E Tests

```bash
npm run test:e2e
```

_Note: Ensure your development server is running (`npm run dev`) before running E2E tests._

---

## 🌟 Best Practices for New Developers

### 1. The "Pure Logic" Rule

Whenever you write complex logic (like filtering data or formatting strings), **extract it into a utility function**.

- **Bad**: Writing filtering logic directly inside a React component.
- **Good**: Moving it to `src/app/(frontend)/utils.ts`.
- **Why**: Utility functions are "pure" and can be tested in milliseconds without setting up a browser environment.

### 2. The AAA Pattern (Assemble, Act, Assert)

Keep your tests readable by following this simple structure:

```typescript
it('should do something correctly', () => {
  // 1. Arrange (Assemble): Set up mock data
  const data = { ... };

  // 2. Act: Call the function
  const result = myFunction(data);

  // 3. Assert: Check the outcome
  expect(result).toBe('expected output');
});
```

### 3. Test for "Sad Paths" 😢

Don't just test when things go right. Test for:

- Missing data (`null` or `undefined`).
- Incorrect data types.
- API failures.
- **Goal**: Ensure the app shows a graceful fallback instead of crashing.

### 4. Continuous Integration (CI)

Run your tests:

1.  **Locally**: Before every commit.
2.  **In CI**: Automatically on every Pull Request to GitHub.

---

## 📁 Testing Folder Structure

- `tests/unit`: Isolated tests for helper functions and logic (very fast).
- `tests/int`: Integration tests that involve the PayloadCMS instance (requires database).
- `tests/e2e`: User flow tests that simulate a real browser (Playwright).

---

## 🗄️ Test Database Files

### What Are They?

When you run integration tests, you'll see temporary database files in your project root:

```
test-*.db       # Random test databases (e.g., test-abc123.db)
test.db         # Generic test database
```

**Why?** Each test run creates a fresh, isolated database to:

- ✅ Prevent database locking issues
- ✅ Avoid interference between test runs
- ✅ Keep your production `payload.db` safe

### Cleanup

**Manual cleanup** (remove all test databases):

```bash
npm run test:clean
```

**Your production database** (`payload.db`) is **never touched** by tests - it's completely safe! 🎉

**Note**: Test databases are automatically ignored by Git (added to `.gitignore`).
