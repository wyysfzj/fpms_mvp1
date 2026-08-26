import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'

const contractUrl = new URL('../../../data/testcases/demo_v6_ui_parity_v1.json', import.meta.url)

const actors = ['HUMAN', 'CODEX', 'STRICT_UI_TECHNICAL']
const classifications = new Set(['EXPLICIT_INPUT', 'SOURCE_BOUND', 'APP_GENERATED'])
const allowedDifferences = [
  'RUN_SUFFIX',
  'UUID_OR_AUTOINCREMENT_ID',
  'DATABASE_OR_FILE_PATH',
  'DYNAMIC_CREDENTIAL',
  'IDEMPOTENCY_KEY',
  'SYSTEM_TIMESTAMP',
]

const label = (role, value) => ({ role, label: value })
const testid = (value) => ({ testid: value })

function input(stage, fieldKey, classification, valueRule, uiRoute, control, sourceSelector, normalization) {
  return {
    stage,
    field_key: fieldKey,
    classification,
    value_rule: valueRule,
    ui_route: uiRoute,
    control,
    source_selector: sourceSelector,
    normalization,
    required: true,
  }
}

function output(stage, fieldKey, classification, valueRule, uiRoute, control, sourceSelector, normalization, observable, expectedRule, uiEvidencePoint) {
  return {
    stage,
    field_key: fieldKey,
    classification,
    value_rule: valueRule,
    ui_route: uiRoute,
    control,
    source_selector: sourceSelector,
    normalization,
    required: true,
    observable,
    expected_rule: expectedRule,
    ui_evidence_point: uiEvidencePoint,
  }
}

function assertionRow(stage, assertionKey, expectedRule, uiEvidencePoint) {
  return {
    stage,
    assertion_key: assertionKey,
    expected_rule: expectedRule,
    ui_evidence_point: uiEvidencePoint,
    required: true,
  }
}

function canonicalFixture() {
  return {
    schema_id: 'fpms.demo-v6-ui-parity/v1',
    actors,
    bindings: [
      { field_key: 'candidate_commit', classification: 'SOURCE_BOUND', value_rule: 'exact 40-character lowercase Git commit from the fresh-run candidate', required: true },
      { field_key: 'bundle_manifest_sha256', classification: 'SOURCE_BOUND', value_rule: 'exact 64-character lowercase SHA-256 from the validated runtime bundle manifest', required: true },
      { field_key: 'authority_sha256', classification: 'SOURCE_BOUND', value_rule: 'exact 64-character lowercase SHA-256 from the validated runtime authority decision', required: true },
      { field_key: 'actor', classification: 'EXPLICIT_INPUT', value_rule: 'exactly one of HUMAN, CODEX, STRICT_UI_TECHNICAL', required: true },
      { field_key: 'run_id', classification: 'APP_GENERATED', value_rule: 'unique run ID generated for this fresh run', required: true },
      { field_key: 'run_root', classification: 'APP_GENERATED', value_rule: 'validated absolute root dedicated to this fresh run', required: true },
    ],
    allowed_differences: allowedDifferences,
    stages: [
      {
        stage: '01',
        inputs: [
          input('01', 'customer_name', 'EXPLICIT_INPUT', '澄岳智造技术（苏州）有限公司', '/clients/new', label('textbox', '客户名称'), 'operator-entered fixed customer name', 'TRIM_EXACT'),
          input('01', 'customer_code', 'EXPLICIT_INPUT', 'CYZN-<run suffix>', '/clients/new', label('textbox', '客户代码'), 'operator-entered run-scoped customer code', 'RUN_SUFFIX_TEMPLATE'),
          input('01', 'customer_email', 'EXPLICIT_INPUT', 'service@chengyue-ip.example', '/clients/new', label('textbox', '邮箱'), 'operator-entered fixed customer email', 'LOWERCASE_EMAIL'),
          input('01', 'contact_name', 'EXPLICIT_INPUT', '周岚', '/clients/:id', label('textbox', '姓名'), 'operator-entered primary contact name', 'TRIM_EXACT'),
          input('01', 'contact_title', 'EXPLICIT_INPUT', '知识产权经理', '/clients/:id', label('textbox', '职务'), 'operator-entered primary contact title', 'TRIM_EXACT'),
          input('01', 'contact_email', 'EXPLICIT_INPUT', 'zhou.lan@chengyue-ip.example', '/clients/:id', label('textbox', '邮箱'), 'operator-entered primary contact email', 'LOWERCASE_EMAIL'),
          input('01', 'contact_is_primary', 'EXPLICIT_INPUT', 'true', '/clients/:id', label('switch', '主联系人'), 'operator selects the primary-contact switch', 'BOOLEAN_EXACT'),
          input('01', 'case_no', 'EXPLICIT_INPUT', 'CYIP-CN-INV-<run suffix>', '/cases/new', label('textbox', '案号'), 'operator-entered run-scoped case number', 'RUN_SUFFIX_TEMPLATE'),
          input('01', 'case_title', 'EXPLICIT_INPUT', '一种柔性制造产线中视觉检测工位的自适应标定方法', '/cases/new', label('textbox', '标题'), 'operator-entered fixed invention title', 'TRIM_EXACT'),
          input('01', 'case_type', 'EXPLICIT_INPUT', 'NORMAL', '/cases/new', label('combobox', '案件类型'), 'operator selects 普通案件', 'ENUM_EXACT'),
          input('01', 'patent_category', 'EXPLICIT_INPUT', 'INV', '/cases/new', label('combobox', '专利类别'), 'operator selects 发明', 'ENUM_EXACT'),
          input('01', 'flow_direction', 'EXPLICIT_INPUT', 'CN_DOMESTIC', '/cases/new', label('combobox', '流程方向'), 'operator selects 中国国内', 'ENUM_EXACT'),
          input('01', 'fee_reduction', 'EXPLICIT_INPUT', '0', '/cases/new', label('combobox', '费用减缓比例'), 'operator selects 不减免（0）', 'DECIMAL_CANONICAL'),
          input('01', 'client_binding', 'SOURCE_BOUND', 'the unique customer created earlier in Stage 01', '/cases/new', label('combobox', '客户'), 'visible customer option matching customer_name and customer_code', 'IDENTITY_EXACT'),
          input('01', 'first_applicant', 'SOURCE_BOUND', 'same customer backfilled as the first applicant', '/cases/new', label('checkbox', '第一申请人'), 'visible applicant row backfilled from current customer master data', 'IDENTITY_EXACT'),
        ],
        outputs: [
          output('01', 'unique_customer_and_primary_contact', 'APP_GENERATED', 'exactly one customer and one primary contact with the canonical values', '/clients/:id', label('tab', '联系人'), 'current customer detail and contact table', 'IDENTITY_AND_COUNT_EXACT', 'customer and primary contact are visible', 'customer_count=1 and primary_contact_count=1', '客户详情/联系人'),
          output('01', 'unique_case', 'APP_GENERATED', 'exactly one case with the canonical case number and title', '/cases/:id', label('heading', '案件详情'), 'current case detail', 'IDENTITY_AND_COUNT_EXACT', 'the created case is visible', 'case_count=1', '案件详情'),
          output('01', 'same_case_primary_contact_and_first_applicant', 'APP_GENERATED', 'the case primary contact and first applicant both bind to the Stage 01 customer/contact identities', '/cases/:id', label('heading', '案件详情'), 'current case parties projection', 'IDENTITY_EXACT', 'case party relationships are visible', 'primary contact and first applicant are unique and same-case', '案件详情/当事人'),
        ],
      },
      {
        stage: '02',
        inputs: [
          input('02', 'current_case', 'SOURCE_BOUND', 'the unique Stage 01 case', '/official-workflows/filing-preparation', label('heading', '新申请递交准备'), 'current case selected from visible case context', 'IDENTITY_EXACT'),
          input('02', 'filing_catalog_60', 'SOURCE_BOUND', 'exactly 60 current runtime filing-catalog entries', '/documents/wizard', label('combobox', '文书模板'), 'visible OFFICIAL_NOTICE_ catalog options from the validated runtime bundle', 'SORTED_IDENTITY_SET'),
        ],
        outputs: [
          output('02', 'same_filing_package', 'APP_GENERATED', 'initial resolve and exact replay return one identical filing package', '/official-workflows/filing-preparation', label('heading', '新申请递交准备'), 'current filing-preparation package', 'IDENTITY_AND_COUNT_EXACT', 'filing package identity is visible', 'package_count=1 and replayed_package_id=package_id', '新申请递交准备/递交准备总览'),
          output('02', 'catalog_execution_boundary', 'SOURCE_BOUND', 'executable catalog rows are enabled and reference-only rows are disabled', '/documents/wizard', label('combobox', '文书模板'), 'visible current 60-row filing catalog', 'ORDER_AND_STATE_EXACT', 'catalog execution boundary is visible', 'OFFICIAL_NOTICE_001 is executable and OFFICIAL_NOTICE_010 is reference-only', '中间文件向导/文书模板'),
        ],
      },
      {
        stage: '03',
        inputs: [
          input('03', 'filing_submission_completed_at', 'EXPLICIT_INPUT', '2026-08-01 09:00:00', '/official-workflows/filing-preparation', label('textbox', '完成时间'), 'operator-entered manual submission completion time', 'ISO_LOCAL_DATETIME_SECONDS'),
          input('03', 'filing_submission_note', 'EXPLICIT_INPUT', '已完成人工递交', '/official-workflows/filing-preparation', label('textbox', '备注'), 'operator-entered manual submission note', 'TRIM_EXACT'),
          input('03', 'filing_final_submission_evidence', 'SOURCE_BOUND', 'current reviewed FILING_FINAL_SUBMISSION evidence', '/official-workflows/filing-preparation', label('combobox', '已复核递交文件'), 'visible same-case reviewed evidence from the current bundle', 'EVIDENCE_IDENTITY_AND_SHA256'),
          input('03', 'filing_receipt_evidence', 'SOURCE_BOUND', 'current reviewed FILING_RECEIPT evidence', '/official-workflows/filing-preparation', label('combobox', '已上传回执附件'), 'visible same-case reviewed receipt evidence from the current bundle', 'EVIDENCE_IDENTITY_AND_SHA256'),
          input('03', 'filing_receipt_no', 'EXPLICIT_INPUT', 'CNIPA-20260802-001', '/official-workflows/filing-preparation', label('textbox', '官方接收案件编号'), 'operator-entered filing receipt number', 'TRIM_EXACT'),
          input('03', 'filing_receipt_received_at', 'EXPLICIT_INPUT', '2026-08-02 10:00:00', '/official-workflows/filing-preparation', label('textbox', '接收时间'), 'operator-entered receipt time', 'ISO_LOCAL_DATETIME_SECONDS'),
          input('03', 'filing_receipt_receiver', 'EXPLICIT_INPUT', '陈思远', '/official-workflows/filing-preparation', label('textbox', '接收人'), 'operator-entered receiver', 'TRIM_EXACT'),
          input('03', 'acceptance_notice_evidence', 'SOURCE_BOUND', 'current reviewed ACCEPTANCE_NOTICE evidence', '/documents/:id', label('combobox', '已复核证据版本'), 'visible same-case reviewed evidence from the current bundle', 'EVIDENCE_IDENTITY_AND_SHA256'),
          input('03', 'preliminary_examination_evidence', 'SOURCE_BOUND', 'current reviewed PRELIMINARY_EXAMINATION_SOURCE evidence', '/documents/:id', label('combobox', '已复核证据版本'), 'visible same-case reviewed evidence from the current bundle', 'EVIDENCE_IDENTITY_AND_SHA256'),
          input('03', 'publication_notice_evidence', 'SOURCE_BOUND', 'current reviewed PUBLICATION_NOTICE evidence', '/documents/:id', label('combobox', '已复核证据版本'), 'visible same-case reviewed evidence from the current bundle', 'EVIDENCE_IDENTITY_AND_SHA256'),
          input('03', 'substantive_examination_evidence', 'SOURCE_BOUND', 'current reviewed SUBSTANTIVE_EXAMINATION_SOURCE evidence', '/documents/:id', label('combobox', '已复核证据版本'), 'visible same-case reviewed evidence from the current bundle', 'EVIDENCE_IDENTITY_AND_SHA256'),
        ],
        outputs: [
          output('03', 'submission_and_receipt_lineage', 'APP_GENERATED', 'manual submission and filing receipt bind to the current reviewed filing evidence', '/official-workflows/filing-preparation', label('heading', '新申请递交准备'), 'current package submission and receipt panels', 'EVIDENCE_CONSUMER_IDENTITY_EXACT', 'submission and receipt lineage is visible', 'one submission and one receipt consume the selected reviewed evidence', '新申请递交准备/递交与回执'),
          output('03', 'acceptance_projection', 'APP_GENERATED', 'acceptance binds to current reviewed ACCEPTANCE_NOTICE evidence', '/cases/:id', label('heading', '案件详情'), 'current lifecycle overlay', 'EVIDENCE_CONSUMER_IDENTITY_EXACT', 'acceptance is visible', 'acceptance evidence identity and digest match', '案件详情/生命周期'),
          output('03', 'preliminary_projection', 'APP_GENERATED', 'preliminary start and pass both bind to current reviewed PRELIMINARY_EXAMINATION_SOURCE evidence', '/cases/:id', label('heading', '案件详情'), 'current lifecycle overlay', 'EVIDENCE_CONSUMER_IDENTITY_EXACT', 'preliminary start and pass are visible', 'both transitions consume the same selected preliminary evidence version', '案件详情/生命周期'),
          output('03', 'publication_and_substantive_projection', 'APP_GENERATED', 'publication and substantive examination bind to their current reviewed evidence', '/cases/:id', label('heading', '案件详情'), 'current lifecycle overlay', 'EVIDENCE_CONSUMER_IDENTITY_EXACT', 'publication and substantive examination are visible', 'each transition consumes its selected evidence identity and digest', '案件详情/生命周期'),
        ],
      },
      {
        stage: '04',
        inputs: [
          input('04', 'oa_sequence', 'EXPLICIT_INPUT', '1', '/documents/new', label('combobox', '文件模板'), 'operator selects first OA notice template', 'INTEGER_EXACT'),
          input('04', 'oa_notice_at', 'EXPLICIT_INPUT', '2026-08-07 09:00:00', '/documents/new', label('textbox', '文书日期'), 'operator-entered first OA notice time', 'ISO_LOCAL_DATETIME_SECONDS'),
          input('04', 'oa_due_date', 'EXPLICIT_INPUT', '2026-09-22', '/documents/new', label('textbox', '官方截止日'), 'operator-entered first OA due date', 'ISO_DATE'),
          input('04', 'oa_notice_evidence', 'SOURCE_BOUND', 'current reviewed OA_NOTICE_1 evidence', '/documents/:id', label('combobox', '已复核证据版本'), 'visible same-case OA_NOTICE_1 evidence from the current bundle', 'EVIDENCE_IDENTITY_AND_SHA256'),
          input('04', 'oa_reply_output_roles', 'SOURCE_BOUND', 'OA_STATEMENT_WORD, OA_STATEMENT_PDF, OA_MODIFIED_CLAIMS for oa_sequence=1', '/official-workflows/oa-reply', label('heading', 'OA答复工作包'), 'visible current-bundle reply outputs for OA sequence 1', 'SORTED_IDENTITY_SET'),
          input('04', 'oa_receipt_evidence', 'SOURCE_BOUND', 'current reviewed OA_RECEIPT_1 evidence', '/official-workflows/oa-reply', label('combobox', '已上传回执附件'), 'visible same-case OA_RECEIPT_1 evidence from the current bundle', 'EVIDENCE_IDENTITY_AND_SHA256'),
          input('04', 'oa_receipt_received_at', 'SOURCE_BOUND', '2026-08-08 10:00:00 from current OA_RECEIPT_1 bundle metadata', '/official-workflows/oa-reply', label('textbox', '接收时间'), 'current reviewed OA_RECEIPT_1 metadata', 'ISO_LOCAL_DATETIME_SECONDS'),
        ],
        outputs: [
          output('04', 'oa1_unique_chain', 'APP_GENERATED', 'one OA1 package, one task, one linked reply, one receipt, and one archive result', '/official-workflows/oa-reply', label('heading', 'OA答复工作包'), 'current OA1 package and task history', 'IDENTITY_AND_COUNT_EXACT', 'OA1 chain is visible', 'each OA1 chain object count equals one and all are same-case', 'OA答复工作包/源官文与回复链'),
          output('04', 'oa1_reply_output_bindings', 'APP_GENERATED', 'all three current-bundle OA1 output roles bind to the OA1 reply', '/official-workflows/oa-reply', label('heading', 'OA答复工作包'), 'visible OA file-role checklist', 'SORTED_IDENTITY_SET', 'OA1 reply role bindings are visible', 'exactly OA_STATEMENT_WORD, OA_STATEMENT_PDF, OA_MODIFIED_CLAIMS are present', 'OA答复工作包/回复文件角色'),
        ],
      },
      {
        stage: '05',
        inputs: [
          input('05', 'oa_sequence', 'EXPLICIT_INPUT', '2', '/documents/new', label('combobox', '文件模板'), 'operator selects second OA notice template', 'INTEGER_EXACT'),
          input('05', 'oa_notice_at', 'EXPLICIT_INPUT', '2026-08-09 09:00:00', '/documents/new', label('textbox', '文书日期'), 'operator-entered second OA notice time', 'ISO_LOCAL_DATETIME_SECONDS'),
          input('05', 'oa_due_date', 'EXPLICIT_INPUT', '2026-10-23', '/documents/new', label('textbox', '官方截止日'), 'operator-entered second OA due date', 'ISO_DATE'),
          input('05', 'oa_notice_evidence', 'SOURCE_BOUND', 'current reviewed OA_NOTICE_2 evidence', '/documents/:id', label('combobox', '已复核证据版本'), 'visible same-case OA_NOTICE_2 evidence from the current bundle', 'EVIDENCE_IDENTITY_AND_SHA256'),
          input('05', 'oa_reply_output_roles', 'SOURCE_BOUND', 'OA_STATEMENT_WORD, OA_STATEMENT_PDF, OA_MODIFIED_CLAIMS for oa_sequence=2', '/official-workflows/oa-reply', label('heading', 'OA答复工作包'), 'visible current-bundle reply outputs for OA sequence 2', 'SORTED_IDENTITY_SET'),
          input('05', 'oa_receipt_evidence', 'SOURCE_BOUND', 'current reviewed OA_RECEIPT_2 evidence', '/official-workflows/oa-reply', label('combobox', '已上传回执附件'), 'visible same-case OA_RECEIPT_2 evidence from the current bundle', 'EVIDENCE_IDENTITY_AND_SHA256'),
          input('05', 'oa_receipt_received_at', 'SOURCE_BOUND', '2026-08-10 10:00:00 from current OA_RECEIPT_2 bundle metadata', '/official-workflows/oa-reply', label('textbox', '接收时间'), 'current reviewed OA_RECEIPT_2 metadata', 'ISO_LOCAL_DATETIME_SECONDS'),
        ],
        outputs: [
          output('05', 'oa2_unique_chain', 'APP_GENERATED', 'one OA2 package, one task, one linked reply, one receipt, and one archive result', '/official-workflows/oa-reply', label('heading', 'OA答复工作包'), 'current OA2 package and task history', 'IDENTITY_AND_COUNT_EXACT', 'OA2 chain is visible', 'each OA2 chain object count equals one and all are same-case', 'OA答复工作包/源官文与回复链'),
          output('05', 'oa_round_identity_separation', 'APP_GENERATED', 'OA2 source, package, task, reply, and receipt identities all differ from OA1', '/cases/:id', label('heading', '案件详情'), 'same-case OA history', 'IDENTITY_DISJOINT', 'both OA rounds are visible', 'OA1 and OA2 histories remain present and identity-disjoint', '案件详情/OA历史'),
        ],
      },
      {
        stage: '06',
        inputs: [
          input('06', 'original_grant_notice_at', 'EXPLICIT_INPUT', '2026-08-11 09:00:00', '/grant-fee/tasks', label('textbox', '文书日期'), 'operator-entered original grant notice time', 'ISO_LOCAL_DATETIME_SECONDS'),
          input('06', 'original_grant_due_date', 'EXPLICIT_INPUT', '2026-11-23', '/grant-fee/tasks', label('textbox', '官方期限'), 'operator-entered original grant due date', 'ISO_DATE'),
          input('06', 'original_grant_evidence', 'SOURCE_BOUND', 'current reviewed GRANT_NOTICE_ORIGINAL evidence', '/grant-fee/tasks', label('combobox', '已复核证据版本'), 'visible same-case original grant evidence from the current bundle', 'EVIDENCE_IDENTITY_AND_SHA256'),
          input('06', 'replacement_grant_notice_at', 'EXPLICIT_INPUT', '2026-08-12 09:00:00', '/grant-fee/tasks', label('textbox', '文书日期'), 'operator-entered replacement grant notice time', 'ISO_LOCAL_DATETIME_SECONDS'),
          input('06', 'replacement_grant_due_date', 'EXPLICIT_INPUT', '2026-11-24', '/grant-fee/tasks', label('textbox', '官方期限'), 'operator-entered replacement grant due date', 'ISO_DATE'),
          input('06', 'replacement_grant_reason', 'EXPLICIT_INPUT', '依据更正通知更新办理登记手续期限', '/grant-fee/tasks', label('textbox', '替换原因'), 'operator-entered fixed replacement reason', 'TRIM_EXACT'),
          input('06', 'replacement_grant_evidence', 'SOURCE_BOUND', 'current reviewed GRANT_NOTICE_REPLACEMENT evidence', '/grant-fee/tasks', label('combobox', '已复核证据版本'), 'visible same-case replacement grant evidence from the current bundle', 'EVIDENCE_IDENTITY_AND_SHA256'),
          input('06', 'current_task_waiting_client', 'SOURCE_BOUND', 'the unique actionable replacement task in WAITING_CLIENT', '/grant-fee/tasks', label('combobox', '客户指示'), 'visible current replacement task row', 'IDENTITY_AND_STATE_EXACT'),
          input('06', 'current_task_instruction', 'EXPLICIT_INPUT', 'PAY', '/grant-fee/tasks', label('button', '记录缴费指示'), 'operator records PAY on the current task only', 'ENUM_EXACT'),
        ],
        outputs: [
          output('06', 'original_task_superseded_read_only', 'APP_GENERATED', 'the original grant task is superseded and exposes no writable action', '/grant-fee/tasks', label('heading', '授权费任务看板'), 'visible original task row', 'IDENTITY_AND_STATE_EXACT', 'original task supersession is visible', 'original task is read-only and non-actionable', '授权费任务看板/原任务'),
          output('06', 'current_task_pay_once', 'APP_GENERATED', 'the replacement task transitions WAITING_CLIENT to PAY exactly once', '/grant-fee/tasks', label('heading', '授权费任务看板'), 'visible current replacement task row', 'IDENTITY_AND_COUNT_EXACT', 'current PAY instruction is visible', 'PAY instruction count=1', '授权费任务看板/当前任务'),
          output('06', 'no_gov_before_confirmation', 'APP_GENERATED', 'no GOV FeeObligation, FeeDraft, or FeeItem exists before Stage 07 confirmation', '/cases/:id', label('heading', '案件详情'), 'same-case fee overview', 'COUNT_EXACT', 'absence of premature GOV objects is visible', 'GOV obligation=0, draft=0, item=0 before confirmation', '案件详情/同案双轨费用概览'),
        ],
      },
      {
        stage: '07',
        inputs: [
          input('07', 'current_grant_task', 'SOURCE_BOUND', 'the unique current PAY replacement grant task', '/grant-fee/tasks', label('textbox', '案件编号'), 'visible current replacement task row', 'IDENTITY_AND_STATE_EXACT'),
          input('07', 'reviewed_replacement_evidence', 'SOURCE_BOUND', 'current reviewed GRANT_NOTICE_REPLACEMENT evidence bound to the task', '/grant-fee/tasks', label('button', '预览官费'), 'visible current task evidence lineage', 'EVIDENCE_IDENTITY_AND_SHA256'),
          input('07', 'rate_book_digest', 'SOURCE_BOUND', 'exact active rate-book SHA-256 shown by the current preview', '/grant-fee/tasks', label('button', '预览官费'), 'visible preview source facts', 'SHA256_LOWERCASE'),
          input('07', 'rate_row_digests', 'SOURCE_BOUND', 'exact per-line rate-row SHA-256 values shown by the current preview', '/grant-fee/tasks', label('button', '预览官费'), 'visible preview rows', 'ORDERED_SHA256_LIST'),
          input('07', 'preview_digest', 'SOURCE_BOUND', 'exact preview SHA-256 returned for the current read-only preview', '/grant-fee/tasks', label('button', '预览官费'), 'visible preview digest', 'SHA256_LOWERCASE'),
          input('07', 'preview_line_amounts', 'SOURCE_BOUND', '900.00 CNY and 50.00 CNY from the current preview rows', '/grant-fee/tasks', label('button', '预览官费'), 'visible preview line amounts', 'ORDERED_DECIMAL_2_LIST'),
          input('07', 'confirmation_time', 'APP_GENERATED', 'system timestamp generated for the confirmation', '/grant-fee/tasks', label('button', '确认并生成官费草单'), 'confirmation response and visible result', 'ISO_SYSTEM_TIMESTAMP'),
          input('07', 'confirmation_idempotency_key', 'APP_GENERATED', 'unique idempotency key generated for this confirmation action', '/grant-fee/tasks', label('button', '确认并生成官费草单'), 'current browser action ledger', 'OPAQUE_IDENTITY'),
        ],
        outputs: [
          output('07', 'gov_preview_total', 'SOURCE_BOUND', '900.00+50.00=950.00 CNY', '/grant-fee/tasks', label('dialog', '授权登记官费预览'), 'visible official-fee preview rows and total', 'DECIMAL_EQUATION_EXACT', 'GOV preview amounts are visible', 'two lines total exactly 950.00 CNY', '授权登记官费预览'),
          output('07', 'unique_gov_obligation_and_draft', 'APP_GENERATED', 'confirmation creates exactly one GOV obligation and one GOV draft', '/fees/drafts/:id', testid('draft-source-facts'), 'current GOV draft source facts', 'IDENTITY_AND_COUNT_EXACT', 'GOV draft and obligation lineage are visible', 'GOV obligation_count=1 and GOV draft_count=1', '费用草稿详情/计算与来源'),
          output('07', 'gov_lines_read_only', 'APP_GENERATED', 'all GOV draft lines are read-only', '/fees/drafts/:id', testid('draft-source-facts'), 'current GOV draft source facts', 'STATE_EXACT', 'GOV read-only boundary is visible', 'no GOV line exposes an edit or adjustment action', '费用草稿详情/官费草单：全部明细只读'),
        ],
      },
      {
        stage: '08',
        inputs: [
          input('08', 'service_item_1', 'EXPLICIT_INPUT', 'FWSQDJ001', '/fees/drafts/new', label('combobox', '服务费项目'), 'operator selects current runtime service item FWSQDJ001', 'ENUM_EXACT'),
          input('08', 'service_item_2', 'EXPLICIT_INPUT', 'FWSQDJ002', '/fees/drafts/new', label('combobox', '服务费项目'), 'operator selects current runtime service item FWSQDJ002', 'ENUM_EXACT'),
          input('08', 'service_item_2_quantity_before', 'EXPLICIT_INPUT', '1', '/fees/drafts/:id', label('spinbutton', '数量'), 'visible current quantity before adjustment', 'INTEGER_EXACT'),
          input('08', 'service_item_2_quantity_after', 'EXPLICIT_INPUT', '2', '/fees/drafts/:id', label('spinbutton', '数量'), 'operator-entered replacement quantity', 'INTEGER_EXACT'),
          input('08', 'service_adjustment_reason', 'EXPLICIT_INPUT', '客户确认增加一份附加文件处理', '/fees/drafts/:id', label('textbox', '调整原因'), 'operator-entered fixed Chinese reason', 'TRIM_EXACT'),
        ],
        outputs: [
          output('08', 'one_gov_and_one_service_draft', 'APP_GENERATED', 'same case has exactly one domain-pure GOV draft and one domain-pure SERVICE draft', '/fees/drafts', label('heading', '费用草稿'), 'visible same-case draft list', 'IDENTITY_AND_COUNT_EXACT', 'both fee-domain drafts are visible', 'GOV draft_count=1 and SERVICE draft_count=1 with no mixed lines', '费用草稿列表'),
          output('08', 'service_adjustment_total', 'APP_GENERATED', 'SERVICE total changes once from 1500.00 to 1800.00 CNY', '/fees/drafts/:id', testid('draft-source-facts'), 'visible SERVICE before/after source facts', 'DECIMAL_TRANSITION_EXACT', 'SERVICE adjustment is visible', 'one adjustment activity and total 1500.00→1800.00 CNY', '费用草稿详情/计算与来源'),
          output('08', 'both_drafts_locked', 'APP_GENERATED', 'GOV and SERVICE drafts both reach LOCKED and remain read-only', '/fees/drafts/:id', label('tab', '概览'), 'visible draft status and controls', 'STATE_EXACT', 'both lock states are visible', 'GOV=LOCKED and SERVICE=LOCKED with no write control', '费用草稿详情/概览'),
        ],
      },
      {
        stage: '09',
        inputs: [
          input('09', 'planned_pay_date', 'EXPLICIT_INPUT', '2026-08-25', '/fee-management/pay-lists', label('textbox', '计划缴费日期'), 'operator-entered planned payment date', 'ISO_DATE'),
          input('09', 'pay_list_remark', 'EXPLICIT_INPUT', '授权登记官费清单', '/fee-management/pay-lists', label('textbox', '备注'), 'operator-entered fixed pay-list remark', 'TRIM_EXACT'),
          input('09', 'gov_line_amounts', 'SOURCE_BOUND', 'the two current GOV draft line amounts 900.00 and 50.00 CNY', '/fee-management/pay-lists/:id', label('heading', '官费清单详情'), 'visible selected GOV draft lines', 'ORDERED_DECIMAL_2_LIST'),
          input('09', 'official_receipt_fields', 'SOURCE_BOUND', 'empty for every GovPayment', '/fee-management/gov-payments/new', label('textbox', '收据号'), 'visible disabled evidence field in demo command mode', 'EMPTY_EXACT'),
          input('09', 'voucher_fields', 'SOURCE_BOUND', 'empty for every GovPayment', '/fee-management/pay-lists/:id', label('heading', '官费清单详情'), 'visible GovPayment evidence projection', 'EMPTY_EXACT'),
          input('09', 'invoice_fields', 'SOURCE_BOUND', 'empty for every GovPayment', '/fee-management/pay-lists/:id', label('heading', '官费清单详情'), 'visible GovPayment evidence projection', 'EMPTY_EXACT'),
        ],
        outputs: [
          output('09', 'one_two_line_pay_list', 'APP_GENERATED', 'exactly one PayList contains exactly the two GOV lines', '/fee-management/pay-lists/:id', label('heading', '官费清单详情'), 'current PayList detail', 'IDENTITY_AND_COUNT_EXACT', 'two-line PayList is visible', 'PayList_count=1 and line_count=2', '官费清单详情/费用行'),
          output('09', 'pending_official_evidence_per_line', 'APP_GENERATED', 'each GOV line has exactly one REGISTERED_PENDING_OFFICIAL_EVIDENCE GovPayment with empty receipt, voucher, and invoice', '/fee-management/pay-lists/:id', label('alert', '已登记，待官方凭证核验'), 'visible GovPayment list', 'IDENTITY_COUNT_AND_STATE_EXACT', 'pending-evidence boundary is visible', 'GovPayment_count_per_line=1 and all evidence fields empty', '官费清单详情/已登记，待官方凭证核验'),
        ],
      },
      {
        stage: '10',
        inputs: [
          input('10', 'bill_no', 'EXPLICIT_INPUT', 'AR-CYZN-<run suffix>', '/billing/bills/new', label('textbox', '账单编号'), 'operator-entered run-scoped bill number', 'RUN_SUFFIX_TEMPLATE'),
          input('10', 'bill_date', 'EXPLICIT_INPUT', '2026-08-25', '/billing/bills/new', label('textbox', '账单日期'), 'operator-entered bill date', 'ISO_DATE'),
          input('10', 'bill_due_date', 'EXPLICIT_INPUT', '2026-09-24', '/billing/bills/new', label('textbox', '到期日'), 'operator-entered bill due date', 'ISO_DATE'),
          input('10', 'service_locked_draft', 'SOURCE_BOUND', 'the unique locked SERVICE draft from Stage 08', '/billing/bills/new', label('combobox', '费用草稿'), 'visible domain-labelled SERVICE draft option', 'IDENTITY_AND_STATE_EXACT'),
          input('10', 'payment_1_amount', 'EXPLICIT_INPUT', '1200.00', '/billing/payments/new', label('spinbutton', '回款金额'), 'operator-entered first payment amount', 'DECIMAL_2'),
          input('10', 'payment_1_date', 'EXPLICIT_INPUT', '2026-08-25', '/billing/payments/new', label('textbox', '收款日期'), 'operator-entered first payment date', 'ISO_DATE'),
          input('10', 'payment_1_method', 'EXPLICIT_INPUT', 'BANK_TRANSFER', '/billing/payments/new', label('combobox', '付款方式'), 'operator selects 银行转账', 'ENUM_EXACT'),
          input('10', 'payment_1_no', 'EXPLICIT_INPUT', 'RCPT-CYZN-<run suffix>-01', '/billing/payments/new', label('textbox', '收款编号'), 'operator-entered first payment reference', 'RUN_SUFFIX_TEMPLATE'),
          input('10', 'payment_1_bank_ref', 'EXPLICIT_INPUT', 'BTR-CYZN-<run suffix>-01', '/billing/payments/new', label('textbox', '银行流水号'), 'operator-entered first bank reference', 'RUN_SUFFIX_TEMPLATE'),
          input('10', 'payment_2_amount', 'SOURCE_BOUND', '600.00 read after refreshing the partially settled bill', '/billing/bills/:id', label('button', '刷新'), 'visible authoritative bill balance after first offset', 'DECIMAL_2'),
          input('10', 'payment_2_date', 'EXPLICIT_INPUT', '2026-08-26', '/billing/payments/new', label('textbox', '收款日期'), 'operator-entered second payment date', 'ISO_DATE'),
          input('10', 'payment_2_method', 'EXPLICIT_INPUT', 'BANK_TRANSFER', '/billing/payments/new', label('combobox', '付款方式'), 'operator selects 银行转账', 'ENUM_EXACT'),
          input('10', 'payment_2_no', 'EXPLICIT_INPUT', 'RCPT-CYZN-<run suffix>-02', '/billing/payments/new', label('textbox', '收款编号'), 'operator-entered second payment reference', 'RUN_SUFFIX_TEMPLATE'),
          input('10', 'payment_2_bank_ref', 'EXPLICIT_INPUT', 'BTR-CYZN-<run suffix>-02', '/billing/payments/new', label('textbox', '银行流水号'), 'operator-entered second bank reference', 'RUN_SUFFIX_TEMPLATE'),
          input('10', 'offset_1_date', 'EXPLICIT_INPUT', '2026-08-25', '/billing/payments', label('textbox', '核销日期'), 'operator-entered first offset date matching payment 1', 'ISO_DATE'),
          input('10', 'offset_2_date', 'EXPLICIT_INPUT', '2026-08-26', '/billing/payments', label('textbox', '核销日期'), 'operator-entered second offset date matching payment 2', 'ISO_DATE'),
        ],
        outputs: [
          output('10', 'bill_settlement_transition', 'APP_GENERATED', 'UNSETTLED→PARTIALLY_SETTLED/600.00→SETTLED/0.00', '/billing/bills/:id', label('heading', '账单详情'), 'visible authoritative bill status and balance', 'STATE_AND_DECIMAL_TRANSITION_EXACT', 'bill settlement transition is visible', 'initial UNSETTLED, after offset 1 PARTIALLY_SETTLED/600.00, after offset 2 SETTLED/0.00', '账单详情/账单结清状态'),
          output('10', 'two_payments_and_offsets', 'APP_GENERATED', 'exactly two Payment objects and two non-reversed valid Offset objects', '/billing/payments', label('heading', '预收款管理报表'), 'visible payment and offset records', 'IDENTITY_AND_COUNT_EXACT', 'two payments and two offsets are visible', 'Payment_count=2 and valid_Offset_count=2', '预收款管理报表/核销记录'),
          output('10', 'payment_offset_bill_equation', 'APP_GENERATED', '1200.00+600.00=1800.00 for Payments, valid Offsets, and Bill', '/billing/bills/:id', label('heading', '账单详情'), 'visible bill items and offset records', 'DECIMAL_EQUATION_EXACT', 'settlement amount equation is visible', 'sum(Payment)=sum(valid Offset)=Bill=1800.00 CNY', '账单详情/抵扣记录'),
        ],
      },
      {
        stage: '11',
        inputs: [],
        outputs: [
          output('11', 'same_case_gov_pending_evidence', 'SOURCE_BOUND', 'same-case GOV draft, PayList, and GovPayments remain pending official evidence', '/cases/:id', label('heading', '案件详情'), 'same-case dual-track fee overview', 'IDENTITY_TOTAL_AND_STATE_EXACT', 'GOV pending-evidence track is visible', 'GOV identities and 950.00 total remain intact and pending official evidence', '案件详情/同案双轨费用概览'),
          output('11', 'same_case_service_settled', 'SOURCE_BOUND', 'same-case SERVICE obligation, draft, Bill, Payments, and Offsets remain fully settled', '/cases/:id', label('heading', '案件详情'), 'same-case dual-track fee overview', 'IDENTITY_TOTAL_AND_STATE_EXACT', 'SERVICE settled track is visible', 'SERVICE identities and 1800.00 total remain intact and Bill is SETTLED/0.00', '案件详情/同案双轨费用概览'),
          output('11', 'cross_track_consistency', 'APP_GENERATED', 'all same-case identities, amounts, and statuses agree without merging GOV and SERVICE facts', '/cases/:id', label('heading', '案件详情'), 'same-case dual-track fee overview and linked normal pages', 'CROSS_PAGE_IDENTITY_TOTAL_AND_STATE_EXACT', 'cross-track summary is visible', 'GOV and SERVICE chains are internally complete, same-case, and domain-separated', '案件详情/同案双轨费用概览'),
        ],
      },
    ],
    strict_assertions: [
      assertionRow('07', 'preview_line_count_at_least_two', 'preview_line_count>=2', '授权登记官费预览/费用行'),
      assertionRow('07', 'preview_source_digests_exact', 'rate_book_digest, every rate_row_digest, and preview_digest are exact', '授权登记官费预览/来源摘要'),
      assertionRow('07', 'preview_read_only_transaction_snapshot', 'before and after preview, one read-only transaction view shows exact unchanged identities/counts for CaseActivityEvent, demo command carrier, FeeObligation, FeeObligationLine, obligation draft/item links, FeeDraft, FeeItem, PayList, and GovPayment', '授权登记官费预览/只读快照'),
      assertionRow('07', 'one_gov_obligation_and_draft_after_confirmation', 'after confirmation exactly one GOV obligation and one GOV draft exist', '费用草稿详情/计算与来源'),
      assertionRow('07', 'gov_preview_amount_equation', '900.00+50.00=950.00', '授权登记官费预览/合计'),

      assertionRow('08', 'one_domain_pure_gov_and_service', 'same case has exactly one GOV and one SERVICE obligation/draft chain and each domain is pure', '案件详情/同案双轨费用概览'),
      assertionRow('08', 'one_adjustment_and_superseding_chain', 'exactly one adjustment activity, one superseding PAY instruction, and one superseding SERVICE obligation exist', '费用草稿详情/计算与来源'),
      assertionRow('08', 'original_service_header_exact', 'original header is exactly SUPERSEDED/PAY/NOT_CREATED/UNPAID/NOT_APPLICABLE', '费用草稿详情/计算与来源'),
      assertionRow('08', 'new_service_header_exact', 'new header is exactly RECOGNIZED/PAY/CREATED/UNPAID/NOT_APPLICABLE', '费用草稿详情/计算与来源'),
      assertionRow('08', 'adjustment_snapshots_and_digests_exact', 'adjustment_before_snapshot/digest equals the original obligation complete line set and adjustment_after_snapshot/digest equals the new obligation complete line set', '费用草稿详情/调整记录'),
      assertionRow('08', 'current_link_ownership_exact', 'original obligation has no current draft/item links and new obligation owns every current link in one-to-one correspondence', '费用草稿详情/关联缴费义务'),
      assertionRow('08', 'service_adjustment_amount_transition', '1500.00→1800.00', '费用草稿详情/计算与来源'),
      assertionRow('08', 'both_locked_drafts_read_only', 'both drafts are read-only after LOCKED', '费用草稿详情/概览'),

      assertionRow('09', 'one_pay_list_with_two_gov_lines', 'exactly one PayList exists and line count equals the two GOV lines', '官费清单详情/费用行'),
      assertionRow('09', 'one_pending_gov_payment_per_line', 'each line has exactly one REGISTERED_PENDING_OFFICIAL_EVIDENCE GovPayment and receipt/voucher/invoice are all empty', '官费清单详情/已登记，待官方凭证核验'),
      assertionRow('09', 'gov_pay_list_payment_totals_equal', 'GOV draft total = PayList total = GovPayment total = 950.00', '官费清单详情/清单金额'),
      assertionRow('09', 'gov_registration_replay_stable', 'replay leaves identities and counts unchanged', '官费清单详情/登记结果'),
      assertionRow('09', 'service_excluded_from_pay_list', 'SERVICE lines do not enter PayList', '官费清单详情/费用行'),

      assertionRow('10', 'service_bill_chain_totals_equal', 'SERVICE superseding obligation payable total = current linked FeeItem total = SERVICE locked draft total = Bill total = 1800.00', '账单详情/账单明细'),
      assertionRow('10', 'payment_registration_does_not_reduce_balance', 'registering the first Payment does not change bill balance', '预收款管理报表/登记回款不等于账单核销'),
      assertionRow('10', 'first_offset_partially_settles', 'after first 1200.00 Offset the bill is PARTIALLY_SETTLED/600.00', '账单详情/账单结清状态'),
      assertionRow('10', 'second_payment_reads_refreshed_balance', 'after page refresh the second Payment reads the authoritative 600.00 balance', '账单详情/刷新余额'),
      assertionRow('10', 'two_payments_two_offsets_final_settled', 'finally exactly two Payments and two valid Offsets exist and the bill is SETTLED/0.00', '预收款管理报表/核销记录'),
      assertionRow('10', 'payment_offset_bill_totals_equal', 'sum of two Payments = sum of two valid Offsets = Bill total = 1800.00', '账单详情/抵扣记录'),
      assertionRow('10', 'gov_excluded_from_bill', 'GOV amount does not enter Bill', '账单详情/账单明细'),

      assertionRow('11', 'original_service_obligation_final_state', 'original SERVICE obligation remains SUPERSEDED/PAY/NOT_CREATED/UNPAID/NOT_APPLICABLE with no current links', '案件详情/同案双轨费用概览'),
      assertionRow('11', 'new_service_obligation_final_state', 'new SERVICE obligation is RECOGNIZED/PAY/CREATED/UNPAID/NOT_APPLICABLE and owns all current links', '案件详情/同案双轨费用概览'),
      assertionRow('11', 'gov_identity_and_total_chain_complete', 'same-case GOV draft/PayList/GovPayment identity and total chain is complete', '案件详情/同案双轨费用概览'),
      assertionRow('11', 'service_identity_and_total_chain_complete', 'same-case SERVICE obligation/draft/Bill/Payment/Offset identity and total chain is complete', '案件详情/同案双轨费用概览'),
      assertionRow('11', 'dual_track_final_statuses', 'GOV still awaits official evidence and SERVICE is settled', '案件详情/同案双轨费用概览'),
      assertionRow('11', 'network_and_console_empty', 'Network and console arrays are empty', 'strict receipt/Network and console arrays'),
      assertionRow('11', 'stage_11_no_new_writes', 'Stage 11 performs no new writes', 'strict receipt/Stage 11 mutation ledger'),
    ],
  }
}

const exactKeys = (value, keys, path) => {
  assert(value && typeof value === 'object' && !Array.isArray(value), `${path} must be an object`)
  assert.deepEqual(Object.keys(value).sort(), [...keys].sort(), `${path} has unknown or missing keys`)
}

function validateRowShape(row, outputRow, path) {
  const keys = ['stage', 'field_key', 'classification', 'value_rule', 'ui_route', 'control', 'source_selector', 'normalization', 'required']
  if (outputRow) keys.push('observable', 'expected_rule', 'ui_evidence_point')
  exactKeys(row, keys, path)
  assert(classifications.has(row.classification), `${path} has unknown classification ${row.classification}`)
  assert.equal(row.required, true, `${path}.required must be true`)
  assert(!row.ui_route.includes('/demo/abc'), `${path}.ui_route must not use /demo/abc`)
  if ('testid' in row.control) exactKeys(row.control, ['testid'], `${path}.control`)
  else exactKeys(row.control, ['role', 'label'], `${path}.control`)
}

function validateContract(actual) {
  const expected = canonicalFixture()
  exactKeys(actual, ['schema_id', 'actors', 'bindings', 'allowed_differences', 'stages', 'strict_assertions'], 'contract')
  assert.equal(actual.schema_id, 'fpms.demo-v6-ui-parity/v1', 'schema_id drift')
  assert.deepEqual(actual.actors, actors, 'actor enum drift')

  assert(Array.isArray(actual.bindings), 'bindings must be an array')
  for (const [index, binding] of actual.bindings.entries()) {
    exactKeys(binding, ['field_key', 'classification', 'value_rule', 'required'], `bindings[${index}]`)
    assert(classifications.has(binding.classification), `bindings[${index}] has unknown classification`)
    assert.equal(binding.required, true, `bindings[${index}].required must be true`)
  }
  assert.deepEqual(actual.bindings, expected.bindings, 'top-level binding drift')
  assert.deepEqual(actual.allowed_differences, allowedDifferences, 'unknown or missing allowed difference')

  assert(Array.isArray(actual.stages), 'stages must be an array')
  assert.deepEqual(actual.stages.map((stage) => stage.stage), ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11'], 'stage coverage/order drift')
  for (const [stageIndex, stage] of actual.stages.entries()) {
    const expectedStage = expected.stages[stageIndex]
    exactKeys(stage, ['stage', 'inputs', 'outputs'], `stages[${stageIndex}]`)
    for (const kind of ['inputs', 'outputs']) {
      assert(Array.isArray(stage[kind]), `stage ${stage.stage} ${kind} must be an array`)
      const seen = new Set()
      for (const [rowIndex, row] of stage[kind].entries()) {
        validateRowShape(row, kind === 'outputs', `stage ${stage.stage} ${kind}[${rowIndex}]`)
        assert.equal(row.stage, stage.stage, `stage ${stage.stage} ${kind}[${rowIndex}] stage drift`)
        assert(!seen.has(row.field_key), `stage ${stage.stage} ${kind} duplicate field ${row.field_key}`)
        seen.add(row.field_key)
      }
      assert.deepEqual(stage[kind].map((row) => row.field_key), expectedStage[kind].map((row) => row.field_key), `stage ${stage.stage} ${kind} missing or extra field`)
      for (const [rowIndex, row] of stage[kind].entries()) {
        const expectedRow = expectedStage[kind][rowIndex]
        assert.equal(row.classification, expectedRow.classification, `stage ${stage.stage} ${kind} ${row.field_key} classification drift`)
        assert.equal(row.ui_route, expectedRow.ui_route, `stage ${stage.stage} ${kind} ${row.field_key} route drift`)
        assert.deepEqual(row.control, expectedRow.control, `stage ${stage.stage} ${kind} ${row.field_key} control drift`)
        assert.deepEqual(row, expectedRow, `stage ${stage.stage} ${kind} ${row.field_key} canonical rule drift`)
      }
    }
  }

  assert(Array.isArray(actual.strict_assertions), 'strict_assertions must be an array')
  const assertionKeys = new Set()
  for (const [index, row] of actual.strict_assertions.entries()) {
    exactKeys(row, ['stage', 'assertion_key', 'expected_rule', 'ui_evidence_point', 'required'], `strict_assertions[${index}]`)
    assert(['07', '08', '09', '10', '11'].includes(row.stage), `strict_assertions[${index}] stage drift`)
    assert.equal(row.required, true, `strict_assertions[${index}].required must be true`)
    const identity = `${row.stage}:${row.assertion_key}`
    assert(!assertionKeys.has(identity), `duplicate strict assertion ${identity}`)
    assertionKeys.add(identity)
  }
  assert.deepEqual(actual.strict_assertions, expected.strict_assertions, 'collapsed, missing, extra, or drifted Stage 07–11 strict assertion')
}

function expectRejected(name, mutate, messagePattern) {
  const fixture = structuredClone(canonicalFixture())
  mutate(fixture)
  assert.throws(() => validateContract(fixture), messagePattern, `${name} must be rejected for its intended reason`)
  console.log(`PASS invalid fixture: ${name}`)
}

expectRejected('missing field', (fixture) => {
  delete fixture.stages[0].inputs[0].normalization
}, /unknown or missing keys/)

expectRejected('duplicate field', (fixture) => {
  fixture.stages[0].inputs.push(structuredClone(fixture.stages[0].inputs[0]))
}, /duplicate field/)

expectRejected('wrong classification', (fixture) => {
  fixture.stages[0].inputs[0].classification = 'SOURCE_BOUND'
}, /classification drift/)

expectRejected('unknown allowed difference', (fixture) => {
  fixture.allowed_differences.push('BUSINESS_DATE')
}, /unknown or missing allowed difference/)

expectRejected('collapsed 07–11 assertion', (fixture) => {
  fixture.strict_assertions = [
    assertionRow('07', 'all_stage_07_to_11_conditions', 'all amounts and statuses are correct', 'strict receipt'),
  ]
}, /collapsed, missing, extra, or drifted/)

try {
  const canonical = JSON.parse(readFileSync(contractUrl, 'utf8'))
  validateContract(canonical)
  console.log(`PASS canonical contract: ${contractUrl.pathname}`)
  console.log('PASS stage coverage: 01,02,03,04,05,06,07,08,09,10,11')
  console.log(`PASS independent strict assertions: ${canonical.strict_assertions.length}`)
} catch (error) {
  console.error(`FAIL canonical contract: ${error.message}`)
  process.exitCode = 1
}
