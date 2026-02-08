import { MigrateUpArgs, MigrateDownArgs, sql } from '@payloadcms/db-sqlite'

export async function up({ db, payload: _payload, req: _req }: MigrateUpArgs): Promise<void> {
  await db.run(sql`CREATE TABLE IF NOT EXISTS \`users_sessions\` (
  	\`_order\` integer NOT NULL,
  	\`_parent_id\` integer NOT NULL,
  	\`id\` text PRIMARY KEY NOT NULL,
  	\`created_at\` text,
  	\`expires_at\` text NOT NULL,
  	FOREIGN KEY (\`_parent_id\`) REFERENCES \`users\`(\`id\`) ON UPDATE no action ON DELETE cascade
  );
  `)
  await db.run(
    sql`CREATE INDEX IF NOT EXISTS \`users_sessions_order_idx\` ON \`users_sessions\` (\`_order\`);`,
  )
  await db.run(
    sql`CREATE INDEX IF NOT EXISTS \`users_sessions_parent_id_idx\` ON \`users_sessions\` (\`_parent_id\`);`,
  )
  await db.run(sql`CREATE TABLE IF NOT EXISTS \`users\` (
  	\`id\` integer PRIMARY KEY NOT NULL,
  	\`updated_at\` text DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')) NOT NULL,
  	\`created_at\` text DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')) NOT NULL,
  	\`email\` text NOT NULL,
  	\`reset_password_token\` text,
  	\`reset_password_expiration\` text,
  	\`salt\` text,
  	\`hash\` text,
  	\`login_attempts\` numeric DEFAULT 0,
  	\`lock_until\` text
  );
  `)
  await db.run(
    sql`CREATE INDEX IF NOT EXISTS \`users_updated_at_idx\` ON \`users\` (\`updated_at\`);`,
  )
  await db.run(
    sql`CREATE INDEX IF NOT EXISTS \`users_created_at_idx\` ON \`users\` (\`created_at\`);`,
  )
  await db.run(sql`CREATE UNIQUE INDEX IF NOT EXISTS \`users_email_idx\` ON \`users\` (\`email\`);`)
  await db.run(sql`CREATE TABLE IF NOT EXISTS \`media\` (
  	\`id\` integer PRIMARY KEY NOT NULL,
  	\`alt\` text NOT NULL,
  	\`updated_at\` text DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')) NOT NULL,
  	\`created_at\` text DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')) NOT NULL,
  	\`url\` text,
  	\`thumbnail_u_r_l\` text,
  	\`filename\` text,
  	\`mime_type\` text,
  	\`filesize\` numeric,
  	\`width\` numeric,
  	\`height\` numeric,
  	\`focal_x\` numeric,
  	\`focal_y\` numeric
  );
  `)
  await db.run(
    sql`CREATE INDEX IF NOT EXISTS \`media_updated_at_idx\` ON \`media\` (\`updated_at\`);`,
  )
  await db.run(
    sql`CREATE INDEX IF NOT EXISTS \`media_created_at_idx\` ON \`media\` (\`created_at\`);`,
  )
  await db.run(
    sql`CREATE UNIQUE INDEX IF NOT EXISTS \`media_filename_idx\` ON \`media\` (\`filename\`);`,
  )
  await db.run(sql`CREATE TABLE IF NOT EXISTS \`authors\` (
  	\`id\` integer PRIMARY KEY NOT NULL,
  	\`name\` text NOT NULL,
  	\`bio\` text,
  	\`avatar_id\` integer,
  	\`updated_at\` text DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')) NOT NULL,
  	\`created_at\` text DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')) NOT NULL,
  	FOREIGN KEY (\`avatar_id\`) REFERENCES \`media\`(\`id\`) ON UPDATE no action ON DELETE set null
  );
  `)
  await db.run(
    sql`CREATE INDEX IF NOT EXISTS \`authors_avatar_idx\` ON \`authors\` (\`avatar_id\`);`,
  )
  await db.run(
    sql`CREATE INDEX IF NOT EXISTS \`authors_updated_at_idx\` ON \`authors\` (\`updated_at\`);`,
  )
  await db.run(
    sql`CREATE INDEX IF NOT EXISTS \`authors_created_at_idx\` ON \`authors\` (\`created_at\`);`,
  )
  await db.run(sql`CREATE TABLE IF NOT EXISTS \`categories\` (
  	\`id\` integer PRIMARY KEY NOT NULL,
  	\`name\` text NOT NULL,
  	\`slug\` text NOT NULL,
  	\`description\` text,
  	\`hero_image_id\` integer,
  	\`color\` text,
  	\`updated_at\` text DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')) NOT NULL,
  	\`created_at\` text DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')) NOT NULL,
  	FOREIGN KEY (\`hero_image_id\`) REFERENCES \`media\`(\`id\`) ON UPDATE no action ON DELETE set null
  );
  `)

  // Patch for existing categories table
  try {
    await db.run(sql`ALTER TABLE \`categories\` ADD COLUMN \`description\` text;`)
  } catch (_e) {
    // Ignore if column exists
  }
  try {
    await db.run(
      sql`ALTER TABLE \`categories\` ADD COLUMN \`hero_image_id\` integer REFERENCES \`media\`(\`id\`);`,
    )
  } catch (_e) {
    // Ignore
  }
  try {
    await db.run(sql`ALTER TABLE \`categories\` ADD COLUMN \`color\` text;`)
  } catch (_e) {
    // Ignore
  }

  await db.run(
    sql`CREATE UNIQUE INDEX IF NOT EXISTS \`categories_slug_idx\` ON \`categories\` (\`slug\`);`,
  )
  await db.run(
    sql`CREATE INDEX IF NOT EXISTS \`categories_hero_image_idx\` ON \`categories\` (\`hero_image_id\`);`,
  )
  await db.run(
    sql`CREATE INDEX IF NOT EXISTS \`categories_updated_at_idx\` ON \`categories\` (\`updated_at\`);`,
  )
  await db.run(
    sql`CREATE INDEX IF NOT EXISTS \`categories_created_at_idx\` ON \`categories\` (\`created_at\`);`,
  )
  await db.run(sql`CREATE TABLE IF NOT EXISTS \`posts\` (
  	\`id\` integer PRIMARY KEY NOT NULL,
  	\`title\` text NOT NULL,
  	\`slug\` text NOT NULL,
  	\`hero_image_id\` integer NOT NULL,
  	\`author_id\` integer NOT NULL,
  	\`category_id\` integer NOT NULL,
  	\`content\` text NOT NULL,
  	\`published_date\` text,
  	\`updated_at\` text DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')) NOT NULL,
  	\`created_at\` text DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')) NOT NULL,
  	FOREIGN KEY (\`hero_image_id\`) REFERENCES \`media\`(\`id\`) ON UPDATE no action ON DELETE set null,
  	FOREIGN KEY (\`author_id\`) REFERENCES \`authors\`(\`id\`) ON UPDATE no action ON DELETE set null,
  	FOREIGN KEY (\`category_id\`) REFERENCES \`categories\`(\`id\`) ON UPDATE no action ON DELETE set null
  );
  `)
  await db.run(sql`CREATE UNIQUE INDEX IF NOT EXISTS \`posts_slug_idx\` ON \`posts\` (\`slug\`);`)
  await db.run(
    sql`CREATE INDEX IF NOT EXISTS \`posts_hero_image_idx\` ON \`posts\` (\`hero_image_id\`);`,
  )
  await db.run(sql`CREATE INDEX IF NOT EXISTS \`posts_author_idx\` ON \`posts\` (\`author_id\`);`)
  await db.run(
    sql`CREATE INDEX IF NOT EXISTS \`posts_category_idx\` ON \`posts\` (\`category_id\`);`,
  )
  await db.run(
    sql`CREATE INDEX IF NOT EXISTS \`posts_updated_at_idx\` ON \`posts\` (\`updated_at\`);`,
  )
  await db.run(
    sql`CREATE INDEX IF NOT EXISTS \`posts_created_at_idx\` ON \`posts\` (\`created_at\`);`,
  )
  await db.run(sql`CREATE TABLE IF NOT EXISTS \`payload_kv\` (
  	\`id\` integer PRIMARY KEY NOT NULL,
  	\`key\` text NOT NULL,
  	\`data\` text NOT NULL
  );
  `)
  await db.run(
    sql`CREATE UNIQUE INDEX IF NOT EXISTS \`payload_kv_key_idx\` ON \`payload_kv\` (\`key\`);`,
  )
  await db.run(sql`CREATE TABLE IF NOT EXISTS \`payload_locked_documents\` (
  	\`id\` integer PRIMARY KEY NOT NULL,
  	\`global_slug\` text,
  	\`updated_at\` text DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')) NOT NULL,
  	\`created_at\` text DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')) NOT NULL
  );
  `)
  await db.run(
    sql`CREATE INDEX IF NOT EXISTS \`payload_locked_documents_global_slug_idx\` ON \`payload_locked_documents\` (\`global_slug\`);`,
  )
  await db.run(
    sql`CREATE INDEX IF NOT EXISTS \`payload_locked_documents_updated_at_idx\` ON \`payload_locked_documents\` (\`updated_at\`);`,
  )
  await db.run(
    sql`CREATE INDEX IF NOT EXISTS \`payload_locked_documents_created_at_idx\` ON \`payload_locked_documents\` (\`created_at\`);`,
  )
  await db.run(sql`CREATE TABLE IF NOT EXISTS \`payload_locked_documents_rels\` (
  	\`id\` integer PRIMARY KEY NOT NULL,
  	\`order\` integer,
  	\`parent_id\` integer NOT NULL,
  	\`path\` text NOT NULL,
  	\`users_id\` integer,
  	\`media_id\` integer,
  	\`authors_id\` integer,
  	\`categories_id\` integer,
  	\`posts_id\` integer,
  	FOREIGN KEY (\`parent_id\`) REFERENCES \`payload_locked_documents\`(\`id\`) ON UPDATE no action ON DELETE cascade,
  	FOREIGN KEY (\`users_id\`) REFERENCES \`users\`(\`id\`) ON UPDATE no action ON DELETE cascade,
  	FOREIGN KEY (\`media_id\`) REFERENCES \`media\`(\`id\`) ON UPDATE no action ON DELETE cascade,
  	FOREIGN KEY (\`authors_id\`) REFERENCES \`authors\`(\`id\`) ON UPDATE no action ON DELETE cascade,
  	FOREIGN KEY (\`categories_id\`) REFERENCES \`categories\`(\`id\`) ON UPDATE no action ON DELETE cascade,
  	FOREIGN KEY (\`posts_id\`) REFERENCES \`posts\`(\`id\`) ON UPDATE no action ON DELETE cascade
  );
  `)
  await db.run(
    sql`CREATE INDEX IF NOT EXISTS \`payload_locked_documents_rels_order_idx\` ON \`payload_locked_documents_rels\` (\`order\`);`,
  )
  await db.run(
    sql`CREATE INDEX IF NOT EXISTS \`payload_locked_documents_rels_parent_idx\` ON \`payload_locked_documents_rels\` (\`parent_id\`);`,
  )
  await db.run(
    sql`CREATE INDEX IF NOT EXISTS \`payload_locked_documents_rels_path_idx\` ON \`payload_locked_documents_rels\` (\`path\`);`,
  )
  await db.run(
    sql`CREATE INDEX IF NOT EXISTS \`payload_locked_documents_rels_users_id_idx\` ON \`payload_locked_documents_rels\` (\`users_id\`);`,
  )
  await db.run(
    sql`CREATE INDEX IF NOT EXISTS \`payload_locked_documents_rels_media_id_idx\` ON \`payload_locked_documents_rels\` (\`media_id\`);`,
  )
  await db.run(
    sql`CREATE INDEX IF NOT EXISTS \`payload_locked_documents_rels_authors_id_idx\` ON \`payload_locked_documents_rels\` (\`authors_id\`);`,
  )
  await db.run(
    sql`CREATE INDEX IF NOT EXISTS \`payload_locked_documents_rels_categories_id_idx\` ON \`payload_locked_documents_rels\` (\`categories_id\`);`,
  )
  await db.run(
    sql`CREATE INDEX IF NOT EXISTS \`payload_locked_documents_rels_posts_id_idx\` ON \`payload_locked_documents_rels\` (\`posts_id\`);`,
  )
  await db.run(sql`CREATE TABLE IF NOT EXISTS \`payload_preferences\` (
  	\`id\` integer PRIMARY KEY NOT NULL,
  	\`key\` text,
  	\`value\` text,
  	\`updated_at\` text DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')) NOT NULL,
  	\`created_at\` text DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')) NOT NULL
  );
  `)
  await db.run(
    sql`CREATE INDEX IF NOT EXISTS \`payload_preferences_key_idx\` ON \`payload_preferences\` (\`key\`);`,
  )
  await db.run(
    sql`CREATE INDEX IF NOT EXISTS \`payload_preferences_updated_at_idx\` ON \`payload_preferences\` (\`updated_at\`);`,
  )
  await db.run(
    sql`CREATE INDEX IF NOT EXISTS \`payload_preferences_created_at_idx\` ON \`payload_preferences\` (\`created_at\`);`,
  )
  await db.run(sql`CREATE TABLE IF NOT EXISTS \`payload_preferences_rels\` (
  	\`id\` integer PRIMARY KEY NOT NULL,
  	\`order\` integer,
  	\`parent_id\` integer NOT NULL,
  	\`path\` text NOT NULL,
  	\`users_id\` integer,
  	FOREIGN KEY (\`parent_id\`) REFERENCES \`payload_preferences\`(\`id\`) ON UPDATE no action ON DELETE cascade,
  	FOREIGN KEY (\`users_id\`) REFERENCES \`users\`(\`id\`) ON UPDATE no action ON DELETE cascade
  );
  `)
  await db.run(
    sql`CREATE INDEX IF NOT EXISTS \`payload_preferences_rels_order_idx\` ON \`payload_preferences_rels\` (\`order\`);`,
  )
  await db.run(
    sql`CREATE INDEX IF NOT EXISTS \`payload_preferences_rels_parent_idx\` ON \`payload_preferences_rels\` (\`parent_id\`);`,
  )
  await db.run(
    sql`CREATE INDEX IF NOT EXISTS \`payload_preferences_rels_path_idx\` ON \`payload_preferences_rels\` (\`path\`);`,
  )
  await db.run(
    sql`CREATE INDEX IF NOT EXISTS \`payload_preferences_rels_users_id_idx\` ON \`payload_preferences_rels\` (\`users_id\`);`,
  )
  await db.run(sql`CREATE TABLE IF NOT EXISTS \`payload_migrations\` (
  	\`id\` integer PRIMARY KEY NOT NULL,
  	\`name\` text,
  	\`batch\` numeric,
  	\`updated_at\` text DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')) NOT NULL,
  	\`created_at\` text DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')) NOT NULL
  );
  `)
  await db.run(
    sql`CREATE INDEX IF NOT EXISTS \`payload_migrations_updated_at_idx\` ON \`payload_migrations\` (\`updated_at\`);`,
  )
  await db.run(
    sql`CREATE INDEX IF NOT EXISTS \`payload_migrations_created_at_idx\` ON \`payload_migrations\` (\`created_at\`);`,
  )
}

export async function down({ db, payload: _payload, req: _req }: MigrateDownArgs): Promise<void> {
  await db.run(sql`DROP TABLE IF EXISTS \`users_sessions\`;`)
  await db.run(sql`DROP TABLE IF EXISTS \`users\`;`)
  await db.run(sql`DROP TABLE IF EXISTS \`media\`;`)
  await db.run(sql`DROP TABLE IF EXISTS \`authors\`;`)
  await db.run(sql`DROP TABLE IF EXISTS \`categories\`;`)
  await db.run(sql`DROP TABLE IF EXISTS \`posts\`;`)
  await db.run(sql`DROP TABLE IF EXISTS \`payload_kv\`;`)
  await db.run(sql`DROP TABLE IF EXISTS \`payload_locked_documents\`;`)
  await db.run(sql`DROP TABLE IF EXISTS \`payload_locked_documents_rels\`;`)
  await db.run(sql`DROP TABLE IF EXISTS \`payload_preferences\`;`)
  await db.run(sql`DROP TABLE IF EXISTS \`payload_preferences_rels\`;`)
  await db.run(sql`DROP TABLE IF EXISTS \`payload_migrations\`;`)
}
