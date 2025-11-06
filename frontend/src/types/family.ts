export interface Family {
  id: number
  owner_id: number
  address?: string
  city?: string
  state?: string
  zip_code?: string
  timezone: string
  budget_monthly?: number
  calendar_ics_url?: string
  partner_email?: string
  created_at: string
  updated_at: string
}

export interface FamilyCreate {
  address?: string
  city?: string
  state?: string
  zip_code?: string
  timezone?: string
  budget_monthly?: number
  calendar_ics_url?: string
  partner_email?: string
}

export interface FamilyUpdate {
  address?: string
  city?: string
  state?: string
  zip_code?: string
  timezone?: string
  budget_monthly?: number
  calendar_ics_url?: string
  partner_email?: string
}

