# Document DB Model (MVP1)

## T_DocTemplate (minimal)
- DocTemplateID, Code, Name, Direction(IN/OUT), Enabled
- Future: triggers TaskTemplateID / FeeDraft rules

## T_Document
- DocumentID, CaseID, DocTemplateID
- Direction, DocDate, Title, RefNo
- CreatedBy/At, UpdatedBy/At

## T_DocAttachment
- AttachmentID, DocumentID
- FileName, FilePath, MimeType, Size
- UploadedBy/At

