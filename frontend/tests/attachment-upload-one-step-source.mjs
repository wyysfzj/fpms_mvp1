import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'

const source = await readFile(
  new URL('../src/modules/documents/components/AttachmentList.vue', import.meta.url),
  'utf8',
)

assert.match(source, /data-testid="attachment-open-upload"/)
assert.match(source, /<el-dialog[\s\S]*data-testid="attachment-upload-dialog"[\s\S]*title="上传附件"/)
assert.match(source, /data-testid="attachment-file-picker"/)
assert.match(source, /label="附件角色"/)
assert.match(source, /label="历史别名（可选）"/)
assert.match(source, /确认上传/)
assert.match(source, /取消/)
assert.match(source, /请先选择文件/)
assert.match(source, /附件上传成功/)

const fileChangeBlock = source.match(/function handleFileChange[\s\S]*?\n}/)?.[0] ?? ''
assert.match(fileChangeBlock, /selectedUploadFile\.value/)
assert.doesNotMatch(fileChangeBlock, /uploadAttachment\(/)

const confirmBlock = source.match(/async function handleUploadConfirm[\s\S]*?\n}/)?.[0] ?? ''
assert.match(confirmBlock, /uploadAttachment\(/)
assert.match(confirmBlock, /uploadDialogVisible\.value = false/)
assert.match(confirmBlock, /resetUploadDraft\(\)/)

const persistentUploadArea =
  source.match(/<div class="attachment-upload">[\s\S]*?<\/div>\n\s*<el-dialog/)?.[0] ?? ''
assert.doesNotMatch(persistentUploadArea, /placeholder="选择附件角色"/)
assert.doesNotMatch(persistentUploadArea, /placeholder="选择历史别名（可选）"/)

