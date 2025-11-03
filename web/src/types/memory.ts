export interface MemorySubmissionData {
  location_id: number
  business_name: string
  start_year?: number
  end_year?: number
  note?: string
  proof_url?: string
}

export interface MemorySubmissionResponse {
  id: number
  location_id: number
  business_name: string
  start_year: number | null
  end_year: number | null
  note: string | null
  proof_url: string | null
  created_at: string
  status: 'pending' | 'approved' | 'rejected'
}

export interface MemoryFormData {
  businessName: string
  startYear: string
  endYear: string
  note: string
  proofUrl: string
}

export interface MemoryFormErrors {
  businessName?: string
  startYear?: string
  endYear?: string
  note?: string
  proofUrl?: string
  _form?: string
}

export type MemoryFormStatus =
  | 'idle'
  | 'validating'
  | 'submitting'
  | 'error'
  | 'success'
