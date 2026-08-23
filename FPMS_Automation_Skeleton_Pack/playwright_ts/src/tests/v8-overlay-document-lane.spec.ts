import { expect, test } from '@playwright/test'
import type { Page, Route } from '@playwright/test'

const caseId = 'case-v8-overlay-document'

test('文件驱动线只展示版本、派生、工作包、回执和任务事实', async ({ page }) => {
    await mockCaseOverlay(page)
    await page.addInitScript(() => {
        window.localStorage.setItem('fpms_token', 'v8-overlay-document-token')
    })
    await page.goto(`/cases/${caseId}`, { waitUntil: 'domcontentloaded' })

    const lane = page.getByTestId('document-evidence-lane')
    await expect(lane.getByRole('heading', { name: '文件驱动' })).toBeVisible()
    await expect(lane.getByText('活动类型：审查意见答复已递交', { exact: true })).toBeVisible()
    await expect(lane.getByText('OA_EXTERNAL_SUBMISSION_RECORDED', { exact: false })).toHaveCount(0)
    await expect(lane.getByText('角色：OFFICIAL_FINAL_PDF', { exact: true })).toBeVisible()
    await expect(lane.getByText('版本：2', { exact: true })).toBeVisible()
    await expect(lane.getByText('复核状态：APPROVED', { exact: true })).toBeVisible()
    await expect(lane.getByText('派生类型：FORMAT_CONVERSION', { exact: true })).toBeVisible()
    await expect(lane.getByText('工作包类型：OA_REPLY', { exact: true })).toBeVisible()
    await expect(lane.getByText('工作包状态：SUBMITTED', { exact: true })).toBeVisible()
    await expect(lane.getByText('回执类型：CNIPA_RECEIPT', { exact: true })).toBeVisible()
    await expect(lane.getByText('归档状态：ARCHIVED', { exact: true })).toBeVisible()
    await expect(lane.getByText('任务状态：DONE', { exact: true })).toBeVisible()
    await expect(lane.getByText('PATENT_IN_FORCE', { exact: false })).toHaveCount(0)
    await expect(lane.getByText('1000.00', { exact: false })).toHaveCount(0)
})

test('未知活动类型显示待确认且不暴露原始枚举', async ({ page }) => {
    await mockCaseOverlay(page, 'UNRECOGNIZED_DOCUMENT_ACTIVITY')
    await page.addInitScript(() => {
        window.localStorage.setItem('fpms_token', 'v8-overlay-document-token')
    })
    await page.goto(`/cases/${caseId}`, { waitUntil: 'domcontentloaded' })

    const lane = page.getByTestId('document-evidence-lane')
    await expect(lane.getByText('活动类型：活动类型待确认', { exact: true })).toBeVisible()
    await expect(lane.getByText('UNRECOGNIZED_DOCUMENT_ACTIVITY', { exact: false })).toHaveCount(0)
})

async function mockCaseOverlay(
    page: Page,
    activityType = 'OA_EXTERNAL_SUBMISSION_RECORDED',
): Promise<void> {
    await page.route('**/api/v1/**', async (route) => {
        const request = route.request()
        const apiPath = new URL(request.url()).pathname.replace(/^\/api\/v1/, '')
        if (request.method() === 'GET' && apiPath === '/auth/me') {
            return fulfillJson(route, {
                permissions: ['Case.Read', 'Doc.Read', 'Task.Read', 'Fee.Read'],
            })
        }
        if (request.method() === 'GET' && apiPath === `/cases/${caseId}`) {
            return fulfillJson(route, {
                id: caseId,
                case_no: 'V8-DOCUMENT-001',
                case_type: 'NORMAL',
                patent_category: 'INV',
                flow_dir: 'CN_DOMESTIC',
                title_cn: '文件驱动线测试',
                status: 'OA1',
                applicants: [],
                inventors: [],
                priorities: [],
                bio_deposits: [],
                agent_splits: [],
            })
        }
        if (request.method() === 'GET' && apiPath === `/cases/${caseId}/lifecycle-overlay`) {
            return fulfillJson(route, overlayResponse(activityType))
        }
        if (request.method() === 'GET' && apiPath === '/tasks') {
            return fulfillJson(route, { items: [], page: 1, page_size: 50, total: 0 })
        }
        return fulfillJson(route, { detail: `未处理的文件线模拟请求：${apiPath}` }, 404)
    })
}

async function fulfillJson(route: Route, body: unknown, status = 200): Promise<void> {
    await route.fulfill({ status, contentType: 'application/json', body: JSON.stringify(body) })
}

function overlayResponse(activityType: string) {
    return {
        case_id: caseId,
        lifecycle_revision: 4,
        generated_at: '2026-08-09T10:00:00Z',
        center_snapshot: {
            business_stage: 'PROSECUTION_MANAGEMENT',
            official_procedure_stage: 'OFFICE_ACTION_RESPONSE',
            legal_status: 'APPLICATION_PENDING',
            effective_at: '2026-08-09T09:00:00Z',
            verification_status: 'CONFIRMED',
            source_event_id: 'activity-document',
        },
        milestones: [
            {
                sequence: 4,
                activity_id: 'activity-document',
                lane: 'DOCUMENT',
                activity_type: activityType,
                source_activity_id: 'activity-source',
                effective_at: '2026-08-09T09:00:00Z',
                confirmation_status: 'CONFIRMED',
                center_changes: {},
                document_evidence: [
                    {
                        version: {
                            evidence_version_id: 'version-final-pdf',
                            case_id: caseId,
                            document_id: 'document-oa-reply',
                            attachment_id: 'attachment-final-pdf',
                            lineage_key: 'oa-reply-lineage',
                            role: 'OFFICIAL_FINAL_PDF',
                            version_number: 2,
                            state: 'FINAL',
                            creator_id: 'user-1',
                            review_state: 'APPROVED',
                            reviewer_id: 'reviewer-1',
                            reviewed_at: '2026-08-09T08:00:00Z',
                            final_submitted_at: '2026-08-09T09:00:00Z',
                            content_hash: 'sha256-final-pdf',
                            is_current: true,
                            is_final: true,
                        },
                        derivations: [
                            {
                                evidence_derivation_id: 'derivation-pdf',
                                case_id: caseId,
                                parent_evidence_version_id: 'version-word',
                                child_evidence_version_id: 'version-final-pdf',
                                derivation_type: 'FORMAT_CONVERSION',
                                actor_id: 'user-1',
                                derived_at: '2026-08-09T08:30:00Z',
                                source_snapshot: 'sha256-source-word',
                            },
                        ],
                    },
                ],
                work_packages: [
                    {
                        package_id: 'package-oa-reply',
                        package_kind: 'OA_REPLY',
                        status: 'SUBMITTED',
                        source_document_id: 'document-oa-notice',
                        reply_document_id: 'document-oa-reply',
                        manifest_evidence_version_ids: ['version-final-pdf'],
                        receipts: [
                            {
                                receipt_id: 'receipt-cnipa',
                                receipt_kind: 'CNIPA_RECEIPT',
                                receipt_attachment_id: 'attachment-receipt',
                                receiving_case_no: 'CN-RECEIVING-001',
                                submitter: 'user-1',
                                received_at: '2026-08-09T09:30:00Z',
                                archive_status: 'ARCHIVED',
                            },
                        ],
                        missing_gate_codes: [],
                    },
                ],
                tasks: [
                    {
                        task_id: 'task-oa-reply',
                        document_id: 'document-oa-reply',
                        task_template_id: 'template-oa-reply',
                        title: '一通答复',
                        due_date: '2026-09-09',
                        internal_due_date: '2026-09-02',
                        status: 'DONE',
                        done_at: '2026-08-09T09:45:00Z',
                    },
                ],
                fee_obligations: [
                    {
                        obligation_id: 'fee-hidden',
                        source_activity_id: 'activity-document',
                        source_document_id: null,
                        source_status: 'VERIFIED',
                        fee_domain: 'GOV',
                        obligation_type: 'HIDDEN',
                        due_date: null,
                        currency: 'CNY',
                        statuses: {
                            estimate_status: null,
                            obligation_status: 'RECOGNIZED',
                            client_instruction_status: 'PENDING',
                            draft_status: 'NOT_CREATED',
                            pay_list_status: 'NOT_CREATED',
                            payment_status: 'UNPAID',
                            official_evidence_status: 'PENDING',
                        },
                        lines: [
                            {
                                line_id: 'line-hidden',
                                fee_code: 'HIDDEN',
                                fee_name: '隐藏费用',
                                fee_year_key: 0,
                                official_full_amount: '1000.00',
                                reduction_ratio: '0.0000',
                                payable_amount: '1000.00',
                                source_amount: null,
                                source_date: null,
                                difference_review_state: 'MATCHED',
                            },
                        ],
                        related_facts: [],
                        supersedes_obligation_id: null,
                        supersede_reason: null,
                    },
                ],
                evidence_summary: [],
                warnings: [],
            },
        ],
        decision_gates: [],
        warnings: [],
        legacy_conflicts: [],
        next_cursor: null,
        has_more: false,
    }
}
