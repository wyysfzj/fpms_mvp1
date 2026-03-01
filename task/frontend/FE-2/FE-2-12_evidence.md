# FE-2-12 Evidence Log

## Commands Executed

### Lint
```bash
cd /Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend
npm run lint
```
**Result:** ✅ Passed

### TypeCheck
```bash
npm run typecheck
```
**Result:** ✅ Passed (vue-tsc --noEmit)

### Build
```bash
npm run build
```
**Result:** ✅ Passed (2.77s)
- Updated chunks:
  - `DocumentDetail-D9dINRq3.js` (6.76 kB, was 4.25 kB)
  - `DocumentDetail-BWgw-Jkk.css` (1.34 kB, was 0.44 kB)
  - `documents-CWNbQ8CE.js` (0.81 kB, was 0.43 kB)

## Files Modified/Created

| File | Action |
|------|--------|
| `src/api/documents.types.ts` | Modified - added `Attachment` interface |
| `src/api/documents.ts` | Modified - added `getAttachments`, `uploadAttachment`, `downloadAttachment` |
| `src/modules/documents/components/AttachmentList.vue` | Created |
| `src/modules/documents/pages/DocumentDetail.vue` | Modified - added AttachmentList |

## Manual Smoke Steps

### 1. View Attachments
- Navigate to `/documents/{id}`
- **Expected:** Attachments section visible in side panel with "No attachments yet" or list of files

### 2. Upload File
- Click "📎 Upload File" button
- Select a file
- **Expected:**
  - Status 201 on `POST /documents/{id}/attachments`
  - Success message "File uploaded successfully"
  - Attachment list refreshes with new file

### 3. Download File
- Click "⬇️ Download" on an attachment
- **Expected:**
  - Status 200 on `GET /documents/{id}/attachments/{att_id}/download`
  - Browser triggers file download with correct filename

### 4. Error Handling (413/422)
- Upload a file exceeding size limit
- **Expected:**
  - Error banner displays with message and `requestId`

## API Assumptions

| Endpoint | Method | Request | Response |
|----------|--------|---------|----------|
| `/documents/{id}/attachments` | GET | - | `Attachment[]` |
| `/documents/{id}/attachments` | POST | `multipart/form-data` with `file` field | `Attachment` |
| `/documents/{id}/attachments/{att_id}/download` | GET | - | `Blob` |
| 413/422 errors | - | - | `{ error: { code, message, details }, requestId }` |
