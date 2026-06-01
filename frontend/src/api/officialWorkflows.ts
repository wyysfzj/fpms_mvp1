import { http } from './http'
import type {
    FilingPreparationChecklistResult,
    FilingPreparationExternalOperationPayload,
    FilingPreparationPackage,
    FilingPreparationRefreshPayload,
    LetterHandoffCreatePayload,
    LetterHandoffPreview,
    LetterHandoffResult,
    LetterHandoffStatusUpdatePayload,
    OaReplyChecklistResult,
    OaReplyLinkDocumentPayload,
    OaReplyPackage,
    OaReplyRefreshPayload,
    OfficialChecklistUpdatePayload,
    OfficialFeeLinkage,
    OfficialWorkPackageArchivePayload,
    OfficialWorkPackageArchiveResult,
    OfficialWorkPackageReceipt,
    OfficialWorkPackageReceiptCreatePayload,
} from './officialWorkflows.types'

export async function getFilingPreparationPackage(
    packageId: string
): Promise<FilingPreparationPackage> {
    const response = await http.get<FilingPreparationPackage>(
        `/official-work-packages/${packageId}/filing-preparation`
    )
    return response.data
}

export async function refreshFilingPreparationPackage(
    packageId: string,
    payload: FilingPreparationRefreshPayload = {}
): Promise<FilingPreparationPackage> {
    const response = await http.post<FilingPreparationPackage>(
        `/official-work-packages/${packageId}/filing-preparation/refresh`,
        payload
    )
    return response.data
}

export async function updateFilingPreparationChecklist(
    packageId: string,
    itemCode: string,
    payload: OfficialChecklistUpdatePayload
): Promise<FilingPreparationChecklistResult> {
    const response = await http.patch<FilingPreparationChecklistResult>(
        `/official-work-packages/${packageId}/filing-preparation/checklist/${itemCode}`,
        payload
    )
    return response.data
}

export async function recordFilingPreparationExternalOperation(
    packageId: string,
    payload: FilingPreparationExternalOperationPayload
): Promise<FilingPreparationChecklistResult> {
    const response = await http.post<FilingPreparationChecklistResult>(
        `/official-work-packages/${packageId}/filing-preparation/external-operations`,
        payload
    )
    return response.data
}

export async function getOaReplyPackage(packageId: string): Promise<OaReplyPackage> {
    const response = await http.get<OaReplyPackage>(
        `/official-work-packages/${packageId}/oa-reply`
    )
    return response.data
}

export async function refreshOaReplyPackage(
    packageId: string,
    payload: OaReplyRefreshPayload = {}
): Promise<OaReplyPackage> {
    const response = await http.post<OaReplyPackage>(
        `/official-work-packages/${packageId}/oa-reply/refresh`,
        payload
    )
    return response.data
}

export async function linkOaReplyDocument(
    packageId: string,
    payload: OaReplyLinkDocumentPayload
): Promise<OaReplyPackage> {
    const response = await http.post<OaReplyPackage>(
        `/official-work-packages/${packageId}/oa-reply/reply-document`,
        payload
    )
    return response.data
}

export async function updateOaReplyChecklist(
    packageId: string,
    itemCode: string,
    payload: OfficialChecklistUpdatePayload
): Promise<OaReplyChecklistResult> {
    const response = await http.patch<OaReplyChecklistResult>(
        `/official-work-packages/${packageId}/oa-reply/checklist/${itemCode}`,
        payload
    )
    return response.data
}

export async function getOfficialFeeLinkage(
    packageId: string
): Promise<OfficialFeeLinkage> {
    const response = await http.get<OfficialFeeLinkage>(
        `/official-work-packages/${packageId}/fee-linkage`
    )
    return response.data
}

export async function createOfficialWorkPackageReceipt(
    packageId: string,
    payload: OfficialWorkPackageReceiptCreatePayload
): Promise<OfficialWorkPackageReceipt> {
    const response = await http.post<OfficialWorkPackageReceipt>(
        `/official-work-packages/${packageId}/receipts`,
        payload
    )
    return response.data
}

export async function archiveOfficialWorkPackage(
    packageId: string,
    payload: OfficialWorkPackageArchivePayload = {}
): Promise<OfficialWorkPackageArchiveResult> {
    const response = await http.post<OfficialWorkPackageArchiveResult>(
        `/official-work-packages/${packageId}/archive`,
        payload
    )
    return response.data
}

export async function getLetterHandoffPreview(
    documentId: string
): Promise<LetterHandoffPreview> {
    const response = await http.get<LetterHandoffPreview>(
        `/official-documents/${documentId}/letter-handoff/preview`
    )
    return response.data
}

export async function createLetterHandoff(
    documentId: string,
    payload: LetterHandoffCreatePayload = {}
): Promise<LetterHandoffResult> {
    const response = await http.post<LetterHandoffResult>(
        `/official-documents/${documentId}/letter-handoff`,
        payload
    )
    return response.data
}

export async function updateLetterHandoffStatus(
    documentId: string,
    handoffId: string,
    payload: LetterHandoffStatusUpdatePayload
): Promise<LetterHandoffResult> {
    const response = await http.patch<LetterHandoffResult>(
        `/official-documents/${documentId}/letter-handoff/${handoffId}/status`,
        payload
    )
    return response.data
}
