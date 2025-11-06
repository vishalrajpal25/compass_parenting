export interface Recommendation {
  id: number
  child_profile_id: number
  activity_id: number
  activity_name: string
  provider_name: string
  total_score: number
  fit_score: number
  practical_score: number
  goals_score: number
  score_details: Record<string, any>
  tier: 'primary' | 'budget_saver' | 'stretch'
  explanation?: string
  why_good_fit?: string[]
  considerations?: string[]
  future_benefits?: string[]
  generated_at: string
}

export interface RecommendationRequest {
  child_profile_id: number
  max_activities?: number
}

