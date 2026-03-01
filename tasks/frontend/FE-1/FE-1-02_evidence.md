# FE-1-02 Evidence Log

## Commands Executed
```bash
npm run lint
npm run typecheck
npm run build
```

## Key Outputs

### Lint
```
> fpms-spa@0.1.0 lint
> eslint . --max-warnings 0
```
(No output = success)

### Typecheck
```
> fpms-spa@0.1.0 typecheck
> vue-tsc --noEmit
```
(No output = success)

### Build
```
> fpms-spa@0.1.0 build
> vite build

vite v5.4.21 building for production...
✓ 1528 modules transformed.
✓ built in 2.35s
```

---

## Manual Verification

### 1. Perms Unknown → All Items Visible
- **Action**: Login and check sidebar (perms will be `null` by default)
- **Expected**: All 7 menu items visible (Dashboard, Cases, Documents, Tasks, Fees, Billing, Settings)

### 2. Perms Mocked → Restricted Items Hidden
- **Action**: In browser console after login:
  ```js
  const auth = window.__pinia.state.value.auth
  auth.perms = ['dashboard:read', 'cases:read']
  ```
- **Expected**: Only Dashboard and Cases visible; other items hidden

### 3. Menu Hover/Active Styling Matches Tokens
- **Hover**: Background `#F8FAFC`, text `var(--color-primary)` (#2563EB)
- **Active**: Background `#EFF6FF`, text `var(--color-primary)` (#2563EB)

---

## Final Confirmation
- `npm run lint` ✅ PASS
- `npm run typecheck` ✅ PASS
- `npm run build` ✅ PASS
