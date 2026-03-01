import { http } from './http'
import type { ConsultingCase, ConsultingCaseCreatePayload } from './consulting.types'

interface BackendConsultingCase {
  id: string
  case_no: string
  case_type: 'CONSULTING' | 'SEARCH'
  status: string
  client_id?: string | null
  title_cn?: string | null
  primary_agent_id?: string | null
  recv_date?: string | null
  created_at: string
}

function mapConsultingCase(input: BackendConsultingCase): ConsultingCase {
  return {
    id: input.id,
    case_no: input.case_no,
    case_type: input.case_type,
    status: input.status,
    client_id: input.client_id ?? undefined,
    title_cn: input.title_cn ?? undefined,
    primary_agent_id: input.primary_agent_id ?? undefined,
    recv_date: input.recv_date ?? undefined,
    created_at: input.created_at,
  }
}

export async function createConsultingCase(
  payload: ConsultingCaseCreatePayload,
): Promise<ConsultingCase> {
  const response = await http.post<BackendConsultingCase>('/consulting/cases', payload)
  return mapConsultingCase(response.data)
}
