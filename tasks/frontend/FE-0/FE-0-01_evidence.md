# FE-0-01 Evidence Log

## Commands Executed
```bash
# In frontend directory
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
(No output means success/no errors)

### Typecheck
```
> fpms-spa@0.1.0 typecheck
> vue-tsc --noEmit
```
(No output means success/no errors)

### Build
```
> fpms-spa@0.1.0 build
> vite build

vite v5.4.21 building for production...
✓ 1518 modules transformed. 
dist/index.html                           0.46 kB │ gzip:   0.30 kB
dist/assets/Dashboard-DhM9-1NJ.js         1.23 kB │ gzip:   0.69 kB
dist/assets/index-nc3h3Pbk.js         1,049.37 kB │ gzip: 347.25 kB
...
✓ built in 2.23s
```

---

## Curl Commands (API Parity)

### Login
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}'
```
**Expected**: 200 OK with `{ "access_token": "...", "token_type": "bearer" }`

### Protected Endpoint (Clients List)
```bash
curl http://localhost:8000/api/v1/clients?page=1\&page_size=1 \
  -H "Authorization: Bearer <TOKEN>"
```
**Expected**: 200 OK with `{ "items": [...], "page": 1, "page_size": 1, "total": N }`

### Unauthorized Access
```bash
curl http://localhost:8000/api/v1/clients?page=1\&page_size=1
```
**Expected**: 401 Unauthorized

---

## Manual Smoke Steps (UI)

1. **Access protected route without login**
   - Navigate to `http://localhost:5173/dashboard`
   - **Expected**: Redirected to `/login`

2. **Login with valid credentials**
   - Enter username/password and click Login
   - **Expected**: Redirected to `/dashboard`, shows client count

3. **Login with invalid credentials**
   - Enter wrong username/password
   - **Expected**: Error message displayed (with requestId if available)

4. **Access login while authenticated**
   - Navigate to `/login` after successful login
   - **Expected**: Redirected to `/dashboard`

5. **Session persistence**
   - Refresh page after login
   - **Expected**: Still on `/dashboard`, session maintained

---

## Final Confirmation
- `npm run lint` ✅ PASS
- `npm run typecheck` ✅ PASS
- `npm run build` ✅ PASS
