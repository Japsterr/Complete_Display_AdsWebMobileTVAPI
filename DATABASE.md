# Digital Signage Platform - Database Documentation

## Overview
This document contains the complete database schema and SQL statements needed to create the Digital Signage Platform database. The system uses SQLite as the default database engine but can be adapted for PostgreSQL or MySQL.

## Database Schema

### Core Tables

#### 1. Plans Table
Defines subscription plans with pricing and feature limitations.

```sql
CREATE TABLE "Plans" (
    "plan_id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "plan_name" VARCHAR(50) NOT NULL UNIQUE,
    "price" DECIMAL(10, 2) NOT NULL,
    "currency" VARCHAR(10) NOT NULL DEFAULT 'ZAR',
    "max_campaigns" INTEGER NOT NULL DEFAULT 3,
    "max_displays" INTEGER NOT NULL DEFAULT 5,
    "max_images" INTEGER NOT NULL DEFAULT 10,
    "max_videos" INTEGER NOT NULL DEFAULT 0,
    "max_users" INTEGER NOT NULL DEFAULT 1,
    "max_storage_gb" REAL NOT NULL DEFAULT 1.0,
    "has_video_support" BOOLEAN NOT NULL DEFAULT FALSE,
    "has_advanced_analytics" BOOLEAN NOT NULL DEFAULT FALSE,
    "has_api_access" BOOLEAN NOT NULL DEFAULT FALSE,
    "has_custom_branding" BOOLEAN NOT NULL DEFAULT FALSE,
    "has_priority_support" BOOLEAN NOT NULL DEFAULT FALSE,
    "has_advanced_scheduling" BOOLEAN NOT NULL DEFAULT FALSE,
    "max_screens" INTEGER NOT NULL DEFAULT 5,
    "has_multi_user" BOOLEAN NOT NULL DEFAULT FALSE,
    "created_at" DATETIME NOT NULL,
    "updated_at" DATETIME NOT NULL
);
```

#### 2. Users Table
Core user authentication with account types and plan assignments.

```sql
CREATE TABLE "Users" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "password" VARCHAR(128) NOT NULL,
    "last_login" DATETIME NULL,
    "is_superuser" BOOLEAN NOT NULL DEFAULT FALSE,
    "email" VARCHAR(254) NOT NULL UNIQUE,
    "account_type" VARCHAR(20) NOT NULL DEFAULT 'personal',
    "plan_id" INTEGER NULL REFERENCES "Plans" ("plan_id") DEFERRABLE INITIALLY DEFERRED,
    "is_active" BOOLEAN NOT NULL DEFAULT TRUE,
    "is_staff" BOOLEAN NOT NULL DEFAULT FALSE,
    "date_joined" DATETIME NOT NULL,
    CONSTRAINT "Users_account_type_valid" CHECK ("account_type" IN ('personal', 'business'))
);

CREATE INDEX "Users_plan_id_idx" ON "Users" ("plan_id");
```

#### 3. UserProfiles Table
Extended user information and contact details.

```sql
CREATE TABLE "UserProfiles" (
    "profile_id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "user_id" INTEGER NOT NULL UNIQUE REFERENCES "Users" ("id") DEFERRABLE INITIALLY DEFERRED,
    "first_name" VARCHAR(100) NULL,
    "last_name" VARCHAR(100) NULL,
    "phone_number" VARCHAR(32) NULL,
    "address_line1" VARCHAR(255) NULL,
    "city" VARCHAR(100) NULL,
    "state_province" VARCHAR(100) NULL,
    "postal_code" VARCHAR(20) NULL,
    "country" VARCHAR(100) NULL
);
```

#### 4. Businesses Table
Business account management for multi-user organizations.

```sql
CREATE TABLE "Businesses" (
    "business_id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "name" VARCHAR(255) NOT NULL,
    "owner_id" INTEGER NOT NULL UNIQUE REFERENCES "Users" ("id") DEFERRABLE INITIALLY DEFERRED,
    "created_at" DATETIME NOT NULL
);
```

#### 5. BusinessMembers Table
Team member management within business accounts.

```sql
CREATE TABLE "BusinessMembers" (
    "member_id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "business_id" INTEGER NOT NULL REFERENCES "Businesses" ("business_id") DEFERRABLE INITIALLY DEFERRED,
    "user_id" INTEGER NOT NULL REFERENCES "Users" ("id") DEFERRABLE INITIALLY DEFERRED,
    "member_role" VARCHAR(20) NOT NULL DEFAULT 'viewer',
    "joined_at" DATETIME NOT NULL,
    CONSTRAINT "BusinessMembers_member_role_valid" CHECK ("member_role" IN ('owner', 'admin', 'editor', 'viewer')),
    UNIQUE ("business_id", "user_id")
);

CREATE INDEX "BusinessMembers_business_id_idx" ON "BusinessMembers" ("business_id");
CREATE INDEX "BusinessMembers_user_id_idx" ON "BusinessMembers" ("user_id");
```

### Content Management Tables

#### 6. Media Table
File storage for images and videos used in campaigns.

```sql
CREATE TABLE "Media" (
    "media_id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "personal_user_id" INTEGER NULL REFERENCES "Users" ("id") DEFERRABLE INITIALLY DEFERRED,
    "business_id" INTEGER NULL REFERENCES "Businesses" ("business_id") DEFERRABLE INITIALLY DEFERRED,
    "uploaded_by_id" INTEGER NOT NULL REFERENCES "Users" ("id") DEFERRABLE INITIALLY DEFERRED,
    "file" VARCHAR(100) NOT NULL,
    "name" VARCHAR(255) NOT NULL,
    "media_type" VARCHAR(10) NOT NULL DEFAULT 'image',
    "description" TEXT NULL,
    "uploaded_at" DATETIME NOT NULL,
    CONSTRAINT "media_owner_xor" CHECK (
        ("personal_user_id" IS NOT NULL AND "business_id" IS NULL) OR
        ("personal_user_id" IS NULL AND "business_id" IS NOT NULL)
    ),
    CONSTRAINT "Media_media_type_valid" CHECK ("media_type" IN ('image', 'video'))
);

CREATE INDEX "Media_personal_user_id_idx" ON "Media" ("personal_user_id");
CREATE INDEX "Media_business_id_idx" ON "Media" ("business_id");
CREATE INDEX "Media_uploaded_by_id_idx" ON "Media" ("uploaded_by_id");
```

#### 7. Campaigns Table
Campaign management with status tracking and scheduling.

```sql
CREATE TABLE "Campaigns" (
    "campaign_id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "personal_user_id" INTEGER NULL REFERENCES "Users" ("id") DEFERRABLE INITIALLY DEFERRED,
    "business_id" INTEGER NULL REFERENCES "Businesses" ("business_id") DEFERRABLE INITIALLY DEFERRED,
    "created_by_id" INTEGER NOT NULL REFERENCES "Users" ("id") DEFERRABLE INITIALLY DEFERRED,
    "name" VARCHAR(255) NOT NULL,
    "description" TEXT NULL,
    "status" VARCHAR(20) NOT NULL DEFAULT 'draft',
    "start_date" DATETIME NULL,
    "end_date" DATETIME NULL,
    "created_at" DATETIME NOT NULL,
    "updated_at" DATETIME NOT NULL,
    CONSTRAINT "campaign_owner_xor" CHECK (
        ("personal_user_id" IS NOT NULL AND "business_id" IS NULL) OR
        ("personal_user_id" IS NULL AND "business_id" IS NOT NULL)
    ),
    CONSTRAINT "Campaigns_status_valid" CHECK ("status" IN ('draft', 'ready', 'active', 'paused', 'scheduled', 'expired'))
);

CREATE INDEX "Campaigns_personal_user_id_idx" ON "Campaigns" ("personal_user_id");
CREATE INDEX "Campaigns_business_id_idx" ON "Campaigns" ("business_id");
CREATE INDEX "Campaigns_created_by_id_idx" ON "Campaigns" ("created_by_id");
```

#### 8. CampaignMedia Table
Links media files to campaigns with display order and duration.

```sql
CREATE TABLE "CampaignMedia" (
    "campaign_media_id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "campaign_id" INTEGER NOT NULL REFERENCES "Campaigns" ("campaign_id") DEFERRABLE INITIALLY DEFERRED,
    "media_id" INTEGER NOT NULL REFERENCES "Media" ("media_id") DEFERRABLE INITIALLY DEFERRED,
    "display_duration_seconds" INTEGER UNSIGNED NOT NULL DEFAULT 10,
    "order" INTEGER UNSIGNED NOT NULL DEFAULT 0,
    UNIQUE ("campaign_id", "media_id", "order")
);

CREATE INDEX "CampaignMedia_campaign_id_idx" ON "CampaignMedia" ("campaign_id");
CREATE INDEX "CampaignMedia_media_id_idx" ON "CampaignMedia" ("media_id");
```

### Display Management Tables

#### 9. Displays Table
Digital signage display devices with activation and ownership.

```sql
CREATE TABLE "Displays" (
    "display_id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "personal_user_id" INTEGER NULL REFERENCES "Users" ("id") DEFERRABLE INITIALLY DEFERRED,
    "business_id" INTEGER NULL REFERENCES "Businesses" ("business_id") DEFERRABLE INITIALLY DEFERRED,
    "registered_by_id" INTEGER NULL REFERENCES "Users" ("id") DEFERRABLE INITIALLY DEFERRED,
    "default_campaign_id" INTEGER NULL REFERENCES "Campaigns" ("campaign_id") DEFERRABLE INITIALLY DEFERRED,
    "name" VARCHAR(255) NOT NULL,
    "location" VARCHAR(255) NULL,
    "device_id" VARCHAR(255) NULL UNIQUE,
    "activation_code" VARCHAR(10) NULL UNIQUE,
    "activation_status" VARCHAR(20) NOT NULL DEFAULT 'pending',
    "last_seen" DATETIME NULL,
    "device_info" JSON NOT NULL DEFAULT '{}',
    "registered_at" DATETIME NOT NULL,
    CONSTRAINT "display_owner_xor" CHECK (
        ("personal_user_id" IS NULL AND "business_id" IS NULL AND "activation_status" = 'pending') OR
        ("personal_user_id" IS NOT NULL AND "business_id" IS NULL) OR
        ("personal_user_id" IS NULL AND "business_id" IS NOT NULL)
    ),
    CONSTRAINT "Displays_activation_status_valid" CHECK ("activation_status" IN ('pending', 'active', 'inactive', 'blocked'))
);

CREATE INDEX "Displays_personal_user_id_idx" ON "Displays" ("personal_user_id");
CREATE INDEX "Displays_business_id_idx" ON "Displays" ("business_id");
CREATE INDEX "Displays_registered_by_id_idx" ON "Displays" ("registered_by_id");
CREATE INDEX "Displays_default_campaign_id_idx" ON "Displays" ("default_campaign_id");
```

#### 10. Schedules Table
Campaign scheduling for specific displays and time periods.

```sql
CREATE TABLE "Schedules" (
    "schedule_id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "display_id" INTEGER NOT NULL REFERENCES "Displays" ("display_id") DEFERRABLE INITIALLY DEFERRED,
    "campaign_id" INTEGER NOT NULL REFERENCES "Campaigns" ("campaign_id") DEFERRABLE INITIALLY DEFERRED,
    "start_datetime" DATETIME NOT NULL,
    "end_datetime" DATETIME NOT NULL,
    "priority" INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX "Schedules_display_id_idx" ON "Schedules" ("display_id");
CREATE INDEX "Schedules_campaign_id_idx" ON "Schedules" ("campaign_id");
```

### Analytics and Tracking Tables

#### 11. DeviceHeartbeats Table
Track device online status and health monitoring.

```sql
CREATE TABLE "DeviceHeartbeats" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "display_id" INTEGER NOT NULL REFERENCES "Displays" ("display_id") DEFERRABLE INITIALLY DEFERRED,
    "timestamp" DATETIME NOT NULL,
    "device_status" VARCHAR(20) NOT NULL DEFAULT 'online',
    "current_campaign_id" INTEGER NULL REFERENCES "Campaigns" ("campaign_id") DEFERRABLE INITIALLY DEFERRED,
    "device_info" JSON NOT NULL DEFAULT '{}'
);

CREATE INDEX "DeviceHeartbeats_display_timestamp_idx" ON "DeviceHeartbeats" ("display_id", "timestamp" DESC);
```

#### 12. MediaImpressions Table
Track individual media display events for analytics.

```sql
CREATE TABLE "MediaImpressions" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "display_id" INTEGER NOT NULL REFERENCES "Displays" ("display_id") DEFERRABLE INITIALLY DEFERRED,
    "campaign_id" INTEGER NOT NULL REFERENCES "Campaigns" ("campaign_id") DEFERRABLE INITIALLY DEFERRED,
    "media_id" INTEGER NOT NULL REFERENCES "Media" ("media_id") DEFERRABLE INITIALLY DEFERRED,
    "started_at" DATETIME NOT NULL,
    "duration_shown" INTEGER NOT NULL,
    "scheduled_duration" INTEGER NOT NULL,
    "completed" BOOLEAN NOT NULL DEFAULT FALSE,
    "sequence_number" INTEGER NOT NULL,
    "total_media_in_campaign" INTEGER NOT NULL
);

CREATE INDEX "MediaImpressions_display_started_idx" ON "MediaImpressions" ("display_id", "started_at" DESC);
CREATE INDEX "MediaImpressions_campaign_started_idx" ON "MediaImpressions" ("campaign_id", "started_at" DESC);
CREATE INDEX "MediaImpressions_media_started_idx" ON "MediaImpressions" ("media_id", "started_at" DESC);
```

#### 13. CampaignSessions Table
Track campaign viewing sessions on devices.

```sql
CREATE TABLE "CampaignSessions" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "display_id" INTEGER NOT NULL REFERENCES "Displays" ("display_id") DEFERRABLE INITIALLY DEFERRED,
    "campaign_id" INTEGER NOT NULL REFERENCES "Campaigns" ("campaign_id") DEFERRABLE INITIALLY DEFERRED,
    "started_at" DATETIME NOT NULL,
    "ended_at" DATETIME NULL,
    "total_impressions" INTEGER NOT NULL DEFAULT 0,
    "total_duration" INTEGER NOT NULL DEFAULT 0,
    "is_active" BOOLEAN NOT NULL DEFAULT TRUE,
    "ended_reason" VARCHAR(50) NOT NULL DEFAULT ''
);

CREATE INDEX "CampaignSessions_display_started_idx" ON "CampaignSessions" ("display_id", "started_at" DESC);
CREATE INDEX "CampaignSessions_campaign_started_idx" ON "CampaignSessions" ("campaign_id", "started_at" DESC);
```

### Subscription and Payment Tables

#### 14. Subscriptions Table
User subscription management and billing periods.

```sql
CREATE TABLE "Subscriptions" (
    "subscription_id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "user_id" INTEGER NOT NULL REFERENCES "Users" ("id") DEFERRABLE INITIALLY DEFERRED,
    "plan_id" INTEGER NOT NULL REFERENCES "Plans" ("plan_id") DEFERRABLE INITIALLY DEFERRED,
    "start_date" DATE NOT NULL,
    "end_date" DATE NULL,
    "is_active" BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE INDEX "Subscriptions_user_id_idx" ON "Subscriptions" ("user_id");
CREATE INDEX "Subscriptions_plan_id_idx" ON "Subscriptions" ("plan_id");
```

#### 15. Payments Table
Payment transaction records.

```sql
CREATE TABLE "Payments" (
    "payment_id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "subscription_id" INTEGER NOT NULL REFERENCES "Subscriptions" ("subscription_id") DEFERRABLE INITIALLY DEFERRED,
    "amount" DECIMAL(10, 2) NOT NULL,
    "currency" VARCHAR(10) NOT NULL DEFAULT 'USD',
    "payment_date" DATETIME NOT NULL,
    "status" VARCHAR(50) NOT NULL
);

CREATE INDEX "Payments_subscription_id_idx" ON "Payments" ("subscription_id");
```

### Stripe Integration Tables

#### 16. StripeCustomers Table
Links users to Stripe customer records.

```sql
CREATE TABLE "StripeCustomers" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "user_id" INTEGER NOT NULL UNIQUE REFERENCES "Users" ("id") DEFERRABLE INITIALLY DEFERRED,
    "stripe_customer_id" VARCHAR(255) NOT NULL UNIQUE,
    "created_at" DATETIME NOT NULL
);
```

#### 17. StripeSubscriptions Table
Tracks Stripe subscription details and status.

```sql
CREATE TABLE "StripeSubscriptions" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "user_id" INTEGER NOT NULL REFERENCES "Users" ("id") DEFERRABLE INITIALLY DEFERRED,
    "stripe_subscription_id" VARCHAR(255) NOT NULL UNIQUE,
    "stripe_customer_id" INTEGER NOT NULL REFERENCES "StripeCustomers" ("id") DEFERRABLE INITIALLY DEFERRED,
    "status" VARCHAR(20) NOT NULL,
    "current_period_start" DATETIME NOT NULL,
    "current_period_end" DATETIME NOT NULL,
    "plan_name" VARCHAR(50) NOT NULL,
    "created_at" DATETIME NOT NULL,
    "updated_at" DATETIME NOT NULL,
    CONSTRAINT "StripeSubscriptions_status_valid" CHECK ("status" IN ('active', 'past_due', 'canceled', 'unpaid', 'trialing', 'incomplete'))
);

CREATE INDEX "StripeSubscriptions_user_id_idx" ON "StripeSubscriptions" ("user_id");
CREATE INDEX "StripeSubscriptions_stripe_customer_id_idx" ON "StripeSubscriptions" ("stripe_customer_id");
```

#### 18. StripePayments Table
Individual Stripe payment tracking.

```sql
CREATE TABLE "StripePayments" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "stripe_payment_intent_id" VARCHAR(255) NOT NULL UNIQUE,
    "stripe_subscription_id" INTEGER NULL REFERENCES "StripeSubscriptions" ("id") DEFERRABLE INITIALLY DEFERRED,
    "user_id" INTEGER NOT NULL REFERENCES "Users" ("id") DEFERRABLE INITIALLY DEFERRED,
    "amount" DECIMAL(10, 2) NOT NULL,
    "currency" VARCHAR(10) NOT NULL DEFAULT 'ZAR',
    "status" VARCHAR(20) NOT NULL,
    "payment_type" VARCHAR(50) NOT NULL DEFAULT 'subscription',
    "created_at" DATETIME NOT NULL,
    "updated_at" DATETIME NOT NULL,
    CONSTRAINT "StripePayments_status_valid" CHECK ("status" IN ('succeeded', 'pending', 'failed', 'canceled', 'requires_action'))
);

CREATE INDEX "StripePayments_stripe_subscription_id_idx" ON "StripePayments" ("stripe_subscription_id");
CREATE INDEX "StripePayments_user_id_idx" ON "StripePayments" ("user_id");
```

### Authentication Tables

#### 19. RefreshTokens Table
JWT refresh token management.

```sql
CREATE TABLE "RefreshTokens" (
    "token_id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "user_id" INTEGER NOT NULL REFERENCES "Users" ("id") DEFERRABLE INITIALLY DEFERRED,
    "token" VARCHAR(255) NOT NULL UNIQUE,
    "created_at" DATETIME NOT NULL,
    "expires_at" DATETIME NOT NULL
);

CREATE INDEX "RefreshTokens_user_id_idx" ON "RefreshTokens" ("user_id");
```

### Django Framework Tables

#### 20. Django Auth Tables
Required Django authentication and permission tables.

```sql
-- Django Content Types
CREATE TABLE "django_content_type" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "app_label" VARCHAR(100) NOT NULL,
    "model" VARCHAR(100) NOT NULL,
    UNIQUE ("app_label", "model")
);

-- Django Migrations
CREATE TABLE "django_migrations" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "app" VARCHAR(255) NOT NULL,
    "name" VARCHAR(255) NOT NULL,
    "applied" DATETIME NOT NULL
);

-- Django Sessions
CREATE TABLE "django_session" (
    "session_key" VARCHAR(40) NOT NULL PRIMARY KEY,
    "session_data" TEXT NOT NULL,
    "expire_date" DATETIME NOT NULL
);

CREATE INDEX "django_session_expire_date_idx" ON "django_session" ("expire_date");

-- Auth Permissions
CREATE TABLE "auth_permission" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "content_type_id" INTEGER NOT NULL REFERENCES "django_content_type" ("id") DEFERRABLE INITIALLY DEFERRED,
    "codename" VARCHAR(100) NOT NULL,
    "name" VARCHAR(255) NOT NULL,
    UNIQUE ("content_type_id", "codename")
);

-- Auth Groups
CREATE TABLE "auth_group" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "name" VARCHAR(150) NOT NULL UNIQUE
);

CREATE TABLE "auth_group_permissions" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "group_id" INTEGER NOT NULL REFERENCES "auth_group" ("id") DEFERRABLE INITIALLY DEFERRED,
    "permission_id" INTEGER NOT NULL REFERENCES "auth_permission" ("id") DEFERRABLE INITIALLY DEFERRED,
    UNIQUE ("group_id", "permission_id")
);

-- User Groups and Permissions
CREATE TABLE "Users_groups" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "user_id" INTEGER NOT NULL REFERENCES "Users" ("id") DEFERRABLE INITIALLY DEFERRED,
    "group_id" INTEGER NOT NULL REFERENCES "auth_group" ("id") DEFERRABLE INITIALLY DEFERRED,
    UNIQUE ("user_id", "group_id")
);

CREATE TABLE "Users_user_permissions" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "user_id" INTEGER NOT NULL REFERENCES "Users" ("id") DEFERRABLE INITIALLY DEFERRED,
    "permission_id" INTEGER NOT NULL REFERENCES "auth_permission" ("id") DEFERRABLE INITIALLY DEFERRED,
    UNIQUE ("user_id", "permission_id")
);
```

## Initial Data Setup

### Default Plans
Insert the default subscription plans.

```sql
INSERT INTO "Plans" (
    "plan_name", "price", "currency", "max_campaigns", "max_displays", 
    "max_images", "max_videos", "max_users", "max_storage_gb",
    "has_video_support", "has_advanced_analytics", "has_api_access",
    "has_custom_branding", "has_priority_support", "has_advanced_scheduling",
    "max_screens", "has_multi_user", "created_at", "updated_at"
) VALUES 
-- Free Plan
('Free', 0.00, 'ZAR', 3, 5, 10, 0, 1, 1.0, 0, 0, 0, 0, 0, 0, 5, 0, datetime('now'), datetime('now')),

-- Starter Plan
('Starter', 99.00, 'ZAR', 10, 15, 50, 10, 3, 5.0, 1, 0, 1, 0, 0, 1, 15, 1, datetime('now'), datetime('now')),

-- Professional Plan
('Professional', 499.00, 'ZAR', -1, -1, -1, -1, -1, 50.0, 1, 1, 1, 1, 1, 1, -1, 1, datetime('now'), datetime('now'));
```

### Create Database Script
Complete script to create the database from scratch.

```bash
#!/bin/bash
# create_database.sh

# For SQLite (default)
echo "Creating SQLite database..."
sqlite3 db.sqlite3 < database_schema.sql

# For PostgreSQL (alternative)
# createdb digital_signage
# psql digital_signage < database_schema_postgres.sql

# For MySQL (alternative)
# mysql -u root -p -e "CREATE DATABASE digital_signage;"
# mysql -u root -p digital_signage < database_schema_mysql.sql

echo "Database created successfully!"
```

## Django Management Commands

### Setup Database
```bash
# Apply all migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Setup pricing plans
python manage.py setup_pricing_plans

# Update campaign statuses (run periodically)
python manage.py update_campaign_status
```

### Backup and Restore
```bash
# Backup SQLite database
cp db.sqlite3 db_backup_$(date +%Y%m%d_%H%M%S).sqlite3

# Restore from backup
cp db_backup_YYYYMMDD_HHMMSS.sqlite3 db.sqlite3

# Export data (JSON)
python manage.py dumpdata > data_backup.json

# Import data (JSON)
python manage.py loaddata data_backup.json
```

## Database Maintenance

### Optimization Queries
```sql
-- Analyze database statistics
ANALYZE;

-- Vacuum database (SQLite)
VACUUM;

-- Check database integrity
PRAGMA integrity_check;

-- View table sizes
SELECT name, COUNT(*) as rows 
FROM sqlite_master 
JOIN (
    SELECT 'Plans' as name, COUNT(*) as count FROM Plans UNION ALL
    SELECT 'Users' as name, COUNT(*) as count FROM Users UNION ALL
    SELECT 'Campaigns' as name, COUNT(*) as count FROM Campaigns UNION ALL
    SELECT 'Media' as name, COUNT(*) as count FROM Media UNION ALL
    SELECT 'Displays' as name, COUNT(*) as count FROM Displays
) counts ON sqlite_master.name = counts.name
WHERE sqlite_master.type = 'table';
```

### Performance Indexes
```sql
-- Additional performance indexes for large datasets
CREATE INDEX IF NOT EXISTS "idx_campaigns_status_dates" ON "Campaigns" ("status", "start_date", "end_date");
CREATE INDEX IF NOT EXISTS "idx_media_impressions_timestamp" ON "MediaImpressions" ("started_at" DESC);
CREATE INDEX IF NOT EXISTS "idx_displays_last_seen" ON "Displays" ("last_seen" DESC);
CREATE INDEX IF NOT EXISTS "idx_users_active_plan" ON "Users" ("is_active", "plan_id");
```

## Environment Configuration

### Database URLs
```python
# settings.py database configuration examples

# SQLite (Development)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# PostgreSQL (Production)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'digital_signage',
        'USER': 'your_db_user',
        'PASSWORD': 'your_db_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# MySQL (Alternative)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'digital_signage',
        'USER': 'your_db_user',
        'PASSWORD': 'your_db_password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

---

## Summary

This database schema supports:
- ✅ Multi-tenant architecture (personal + business accounts)
- ✅ Subscription-based pricing with feature limitations
- ✅ Campaign management with automatic status updates
- ✅ Device activation and management
- ✅ Media file organization and display scheduling
- ✅ Comprehensive analytics and tracking
- ✅ Stripe payment integration
- ✅ JWT authentication with refresh tokens
- ✅ Full audit trail and session tracking

**Total Tables:** 19 application tables + Django framework tables  
**Database Size:** Scales from development (SQLite) to production (PostgreSQL/MySQL)  
**Features:** Complete digital signage platform with subscription management
