# Templates & Letterhead (MVP1)

## Purpose
Provide template metadata and server-side rendering for documents such as bills and task sheets.

## Tables
- T_Template
- T_LetterHead
- T_SystemParam (partial)

## MVP1 Implementation
- Template files stored under `storage/templates/`
- Admin uploads/updates template metadata (file path)
- Rendering endpoint builds context and uses docxtpl to generate `.docx`

