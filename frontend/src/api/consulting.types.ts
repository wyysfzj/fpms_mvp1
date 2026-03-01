export type ConsultingCaseType = 'CONSULTING' | 'SEARCH'

export interface ConsultingCaseCreatePayload {
  case_no: string
  case_type: ConsultingCaseType
  client_id: string
  title_cn: string
  primary_agent_id: string
  recv_date: string
}

export interface ConsultingCase {
  id: string
  case_no: string
  case_type: ConsultingCaseType
  status: string
  client_id?: string
  title_cn?: string
  primary_agent_id?: string
  recv_date?: string
  created_at: string
}
