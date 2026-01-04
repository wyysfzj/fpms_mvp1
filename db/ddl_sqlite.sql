-- SQLite reference DDL

-- MVP1 Reference DDL (PostgreSQL)
-- Source of truth: Alembic migrations.
-- This SQL is for review / DBA discussion.

-- Consider enabling uuid-ossp if you want DB-generated UUIDs:
-- CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS t_user (
  id VARCHAR(36) PRIMARY KEY,
  username VARCHAR(64) NOT NULL UNIQUE,
  display_name VARCHAR(128),
  password_hash VARCHAR(255) NOT NULL,
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS t_role (
  id VARCHAR(36) PRIMARY KEY,
  code VARCHAR(64) NOT NULL UNIQUE,
  name VARCHAR(128) NOT NULL
);

CREATE TABLE IF NOT EXISTS t_user_role (
  user_id VARCHAR(36) NOT NULL REFERENCES t_user(id) ON DELETE CASCADE,
  role_id VARCHAR(36) NOT NULL REFERENCES t_role(id) ON DELETE CASCADE,
  PRIMARY KEY (user_id, role_id)
);

CREATE TABLE IF NOT EXISTS t_client (
  id VARCHAR(36) PRIMARY KEY,
  client_code VARCHAR(64) UNIQUE,
  name_cn VARCHAR(256) NOT NULL,
  name_en VARCHAR(256),
  client_type VARCHAR(32) NOT NULL DEFAULT 'CLIENT',
  default_currency VARCHAR(8) NOT NULL DEFAULT 'CNY',
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS t_case (
  id VARCHAR(36) PRIMARY KEY,
  case_no VARCHAR(64) NOT NULL UNIQUE,
  case_type VARCHAR(32) NOT NULL DEFAULT 'NORMAL',
  patent_category VARCHAR(32) NOT NULL DEFAULT 'INV',
  flow_dir VARCHAR(32) NOT NULL DEFAULT 'CN_DOMESTIC',
  client_id VARCHAR(36) REFERENCES t_client(id),
  title_cn TEXT,
  title_en TEXT,
  app_no VARCHAR(64),
  status VARCHAR(32) NOT NULL DEFAULT 'NOT_FILED',
  recv_date DATE,
  filing_date DATE,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_case_client ON t_case(client_id);
CREATE INDEX IF NOT EXISTS idx_case_appno ON t_case(app_no);
