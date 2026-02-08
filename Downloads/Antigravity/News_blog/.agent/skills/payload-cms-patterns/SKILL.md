---
description: PayloadCMS collection schema patterns, validation, hooks, and best practices for the News Blog project.
---

# PayloadCMS Patterns

You are working with PayloadCMS 3.73.0 as the headless CMS for a News Blog. Follow these patterns to maintain consistency and prevent breaking changes.

## 🏗️ Collection Schema Conventions

### Required Fields Pattern

Every collection should follow this standard structure:

```typescript
import type { CollectionConfig } from 'payload'

export const CollectionName: CollectionConfig = {
  slug: 'collection-name',
  admin: {
    useAsTitle: 'name', // Field to display in admin UI
    defaultColumns: ['name', 'slug', 'status'], // Columns in list view
  },
  access: {
    read: () => true, // Public read access for frontend
  },
  fields: [
    {
      name: 'name',
      type: 'text',
      required: true,
    },
    {
      name: 'slug',
      type: 'text',
      required: true,
      unique: true, // ALWAYS add unique constraint for slugs
    },
    // ... other fields
  ],
}
```

### Field Naming Conventions

- **Slugs**: Always `slug` (lowercase, singular)
- **Titles/Names**: Use `title` for posts, `name` for taxonomies
- **Relationships**: Use singular form (`author`, not `authors`) unless `hasMany: true`
- **Media**: Use descriptive names (`heroImage`, `thumbnail`, `avatar`)

### Admin Configuration

**Always include**:

- `useAsTitle`: Field to identify records in admin UI
- `defaultColumns`: Most important fields for list view (3-5 columns max)

**Example**:

```typescript
admin: {
  useAsTitle: 'title',
  defaultColumns: ['title', 'author', 'category', 'publishedDate'],
}
```

## 🔗 Relationship Patterns

### One-to-Many Relationships

```typescript
// Post belongs to one Author
{
  name: 'author',
  type: 'relationship',
  relationTo: 'authors',
  required: true, // Enforce data integrity
}

// Post belongs to one Category
{
  name: 'category',
  type: 'relationship',
  relationTo: 'categories',
  required: true,
}
```

### Many-to-Many Relationships

```typescript
// Post can have multiple tags
{
  name: 'tags',
  type: 'relationship',
  relationTo: 'tags',
  hasMany: true,
  required: false,
}
```

### Upload Relationships

```typescript
// Media upload field
{
  name: 'heroImage',
  type: 'upload',
  relationTo: 'media',
  required: true,
}
```

### Handling Populated vs ID References

**Problem**: PayloadCMS can return relationships as objects or IDs depending on `depth` parameter.

**Solution**: Always handle both cases in utility functions.

```typescript
// ✅ Good: Handle both cases
export function getCategoryId(category: Post['category']): string | null {
  // Case 1: Populated object
  if (typeof category === 'object' && category !== null && 'id' in category) {
    return category.id
  }

  // Case 2: ID string
  if (typeof category === 'string') {
    return category
  }

  return null
}
```

## ✅ Validation Patterns

### Built-in Validation

```typescript
{
  name: 'email',
  type: 'email', // Built-in email validation
  required: true,
}

{
  name: 'slug',
  type: 'text',
  required: true,
  unique: true, // Database-level uniqueness
}
```

### Custom Validation

```typescript
{
  name: 'publishedDate',
  type: 'date',
  required: true,
  validate: (value) => {
    const date = new Date(value)
    const now = new Date()

    if (date > now) {
      return 'Published date cannot be in the future'
    }

    return true
  },
}
```

### Field Descriptions

**Always add descriptions for non-obvious fields**:

```typescript
{
  name: 'color',
  type: 'text',
  required: false,
  admin: {
    description: 'Accent color for this category (hex code, e.g., #FF6B6B)',
  },
}
```

## 🪝 Hook Patterns

### Auto-Generate Slugs

```typescript
import { slugify } from '@/utils/slugify'

export const Posts: CollectionConfig = {
  slug: 'posts',
  hooks: {
    beforeChange: [
      ({ data }) => {
        // Auto-generate slug from title if not provided
        if (data.title && !data.slug) {
          data.slug = slugify(data.title)
        }
        return data
      },
    ],
  },
  // ... fields
}
```

### Set Default Values

```typescript
hooks: {
  beforeChange: [
    ({ data, operation }) => {
      // Set publishedDate to now if creating new post
      if (operation === 'create' && !data.publishedDate) {
        data.publishedDate = new Date().toISOString()
      }
      return data
    },
  ],
}
```

### Transform Data on Read

```typescript
hooks: {
  afterRead: [
    ({ doc }) => {
      // Add computed field
      doc.readingTime = calculateReadingTime(doc.content)
      return doc
    },
  ],
}
```

## 🔒 Access Control Patterns

### Public Read, Admin Write

**Standard pattern for blog content**:

```typescript
access: {
  read: () => true, // Anyone can read
  create: ({ req: { user } }) => !!user, // Only authenticated users can create
  update: ({ req: { user } }) => !!user,
  delete: ({ req: { user } }) => !!user,
}
```

### Role-Based Access

```typescript
access: {
  read: () => true,
  create: ({ req: { user } }) => {
    // Only admins can create
    return user?.role === 'admin'
  },
  update: ({ req: { user }, id }) => {
    // Authors can update their own posts
    if (user?.role === 'admin') return true
    return user?.id === id
  },
}
```

## 🗄️ Current Collections

### Posts

**Purpose**: Blog post content  
**Key Fields**: `title`, `slug`, `heroImage`, `author`, `category`, `content`, `publishedDate`  
**Relationships**: Author (required), Category (required), HeroImage (required)

### Authors

**Purpose**: Content creators  
**Key Fields**: `name`, `slug`, `bio`, `avatar`  
**Relationships**: Avatar (optional)

### Categories

**Purpose**: Post taxonomy  
**Key Fields**: `name`, `slug`, `description`, `heroImage`, `color`  
**Relationships**: HeroImage (optional)

### Media

**Purpose**: Image and file uploads  
**Key Fields**: Auto-generated by PayloadCMS  
**Usage**: Referenced by Posts, Categories, Authors

### Users

**Purpose**: Admin authentication  
**Key Fields**: `email`, `password`  
**Usage**: Admin panel access

## 🚫 Breaking Change Prevention

### Never Remove Required Fields

**❌ Bad**:

```typescript
// Removing required field breaks existing data
fields: [
  // { name: 'author', type: 'relationship', relationTo: 'authors', required: true }, // REMOVED
]
```

**✅ Good**:

```typescript
// Make optional first, then remove in next version
fields: [
  { name: 'author', type: 'relationship', relationTo: 'authors', required: false }, // Step 1
]
```

### Add New Fields as Optional

**✅ Good**:

```typescript
// New field is optional
{
  name: 'subtitle',
  type: 'text',
  required: false, // Safe to add
}
```

### Use Migrations for Schema Changes

**Document schema changes**:

```typescript
// migrations/2026-02-08-add-subtitle.ts
export async function up() {
  // Add subtitle field to all posts
  await payload.update({
    collection: 'posts',
    where: {},
    data: { subtitle: '' },
  })
}
```

## 📊 Query Optimization

### Use `depth` Parameter

```typescript
// ✅ Good: Limit depth to avoid over-fetching
const posts = await payload.find({
  collection: 'posts',
  depth: 1, // Only populate first level of relationships
})

// ❌ Bad: Default depth fetches everything
const posts = await payload.find({
  collection: 'posts',
  // depth defaults to 2, may over-fetch
})
```

### Use `select` for Specific Fields

```typescript
// ✅ Good: Only fetch needed fields
const posts = await payload.find({
  collection: 'posts',
  select: {
    title: true,
    slug: true,
    publishedDate: true,
  },
})
```

### Use `where` for Filtering

```typescript
// ✅ Good: Filter at database level
const posts = await payload.find({
  collection: 'posts',
  where: {
    category: {
      equals: categoryId,
    },
  },
})

// ❌ Bad: Fetch all then filter in JavaScript
const allPosts = await payload.find({ collection: 'posts' })
const filtered = allPosts.docs.filter((p) => p.category === categoryId)
```

## 🧪 Testing Collections

### Integration Test Pattern

```typescript
import { describe, it, expect, beforeAll } from 'vitest'
import { getPayload } from 'payload'
import config from '@/payload.config'

describe('Posts Collection', () => {
  let payload

  beforeAll(async () => {
    payload = await getPayload({ config })
  })

  it('should enforce required fields', async () => {
    await expect(
      payload.create({
        collection: 'posts',
        data: { title: 'Test' }, // Missing required fields
      }),
    ).rejects.toThrow()
  })

  it('should enforce unique slug constraint', async () => {
    await payload.create({
      collection: 'posts',
      data: { title: 'Test', slug: 'test-slug' /* ... */ },
    })

    await expect(
      payload.create({
        collection: 'posts',
        data: { title: 'Test 2', slug: 'test-slug' /* ... */ },
      }),
    ).rejects.toThrow()
  })
})
```

## 📚 Related Documentation

- [ADR-001: PayloadCMS Selection](../docs/adr/ADR-001-payloadcms.md)
- [ADR-002: SQLite Database](../docs/adr/ADR-002-sqlite.md)
- [Coding Standards](../docs/CODING_STANDARDS.md)

## 🔗 References

- [PayloadCMS Collections](https://payloadcms.com/docs/configuration/collections)
- [PayloadCMS Hooks](https://payloadcms.com/docs/hooks/overview)
- [PayloadCMS Access Control](https://payloadcms.com/docs/access-control/overview)
