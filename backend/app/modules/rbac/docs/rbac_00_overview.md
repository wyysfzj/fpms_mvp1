# RBAC Module (MVP1)

## Purpose
Provide stable permission enforcement and menu visibility rules.

## MVP1 implementation options
Option A (simplest): roles mapped to permission codes in code (seed at startup).
Option B (recommended): persist Role + Perm in DB to allow Admin tuning.

MVP1 can start with A, but DB tables for B should exist to support future upgrade.

## API (Admin)
- CRUD roles
- assign roles to users
- manage role permissions

