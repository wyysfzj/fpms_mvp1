type TermRule = {
    uiShort: string
    domain: string
    bannedInUi: readonly string[]
    note: string
}

/**
 * 前端术语词典。
 * 用于冻结高频业务术语，避免页面文案再次出现同义词混用。
 */
export const TERM_RULES = {
    caseObject: {
        uiShort: '案件',
        domain: '案件',
        bannedInUi: ['案卷'],
        note: '新版主 UI 统一使用“案件”；“案卷”仅保留为旧系统兼容术语。',
    },
    caseParticipants: {
        uiShort: '申请人/发明人',
        domain: '申请人/发明人（当前页签内容）',
        bannedInUi: ['权利要求'],
        note: '当前页签展示的是申请人和发明人，不是权利要求文本或权项结构。',
    },
    correspondence: {
        uiShort: '往来文件',
        domain: '中间文件与往来管理',
        bannedInUi: ['中间文件', '公文记录', '官方文件'],
        note: '前端展示层统一使用“往来文件”；规格和实施文档可保留“中间文件”领域术语。',
    },
    billingAndReceipts: {
        uiShort: '账单与收款',
        domain: '账单与收款（含收款摘要）',
        bannedInUi: ['账务'],
        note: '当前页面能力覆盖账单与收款结果，不应夸大为完整账务台账。',
    },
} as const satisfies Record<string, TermRule>

export const TERM_UI = {
    caseObject: TERM_RULES.caseObject.uiShort,
    caseParticipants: TERM_RULES.caseParticipants.uiShort,
    correspondence: TERM_RULES.correspondence.uiShort,
    billingAndReceipts: TERM_RULES.billingAndReceipts.uiShort,
    receiptSummary: '收款摘要',
    documentsModule: '文档管理',
} as const

export const TERM_DOMAIN = {
    caseObject: TERM_RULES.caseObject.domain,
    caseParticipants: TERM_RULES.caseParticipants.domain,
    correspondence: TERM_RULES.correspondence.domain,
    billingAndReceipts: TERM_RULES.billingAndReceipts.domain,
} as const

/**
 * 新 UI 文案不得再直接使用这些词；如命中，应替换为 map 中的推荐口径。
 */
export const UI_BANNED_TERM_MAP = {
    案卷: TERM_UI.caseObject,
    权利要求: TERM_UI.caseParticipants,
    中间文件: TERM_UI.correspondence,
    公文记录: TERM_UI.correspondence,
    官方文件: TERM_UI.correspondence,
    账务: TERM_UI.billingAndReceipts,
} as const

export function isBannedUiTerm(term: string): term is keyof typeof UI_BANNED_TERM_MAP {
    return term in UI_BANNED_TERM_MAP
}

export function getPreferredUiTerm(term: string): string | null {
    return UI_BANNED_TERM_MAP[term as keyof typeof UI_BANNED_TERM_MAP] ?? null
}
