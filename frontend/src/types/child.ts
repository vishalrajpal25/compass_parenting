export interface Temperament {
  big_five: {
    openness: number
    conscientiousness: number
    extraversion: number
    agreeableness: number
    neuroticism: number
  }
  sensory_sensitivity: 'low' | 'medium' | 'high'
  intensity_preference: 'low' | 'moderate' | 'high'
  social_preference: 'solo' | 'small_group' | 'team'
}

export interface ScheduleWindow {
  day: 'monday' | 'tuesday' | 'wednesday' | 'thursday' | 'friday' | 'saturday' | 'sunday'
  start: string // HH:MM format
  end: string // HH:MM format
}

export interface Constraints {
  schedule_windows?: ScheduleWindow[]
  max_activities_per_week?: number
  special_needs?: string
  dietary_restrictions?: string
  medical_notes?: string
  neurodiversity_notes?: string
}

export interface ChildProfile {
  id: number
  family_id: number
  name: string
  birth_date: string
  age: number
  temperament?: Temperament
  primary_goal?: string
  secondary_goal?: string
  tertiary_goal?: string
  custom_goals?: string[]
  constraints?: Constraints
  preferred_activity_types?: string[]
  notes?: string
  created_at: string
  updated_at: string
}

export interface ChildProfileCreate {
  name: string
  birth_date: string // YYYY-MM-DD
  temperament?: Temperament
  primary_goal?: string
  secondary_goal?: string
  tertiary_goal?: string
  custom_goals?: string[]
  constraints?: Constraints
  preferred_activity_types?: string[]
  notes?: string
}

export interface ChildProfileUpdate {
  name?: string
  birth_date?: string
  temperament?: Temperament
  primary_goal?: string
  secondary_goal?: string
  tertiary_goal?: string
  custom_goals?: string[]
  constraints?: Constraints
  preferred_activity_types?: string[]
  notes?: string
}

