/**
 * Core type definitions for Intelli-Credit frontend
 */

export interface Application {
  application_id: string
  company_id: string
  company_name?: string
  loan_amount_requested: number
  loan_purpose: string
  submitted_date: string
  status: 'pending' | 'processing' | 'completed' | 'rejected' | 'approved'
  risk_level?: 'high' | 'medium' | 'low'
  created_at: string
  updated_at: string
}

export interface Company {
  company_id: string
  cin: string
  gstin: string
  name: string
  industry: string
  incorporation_date: string
}

export interface FiveCsScores {
  character_score: number
  capacity_score: number
  capital_score: number
  collateral_score: number
  conditions_score: number
}

export interface CreditAssessment {
  id: string
  application_id: string
  risk_score: number
  risk_level: 'high' | 'medium' | 'low'
  five_cs_scores: FiveCsScores
  max_loan_amount: number
  recommended_rate: number
  created_at: string
}

export interface RiskScore {
  overall_score: number
  risk_level: 'high' | 'medium' | 'low'
  top_risk_factors: string[]
  top_positive_factors: string[]
}

export interface LoanRecommendation {
  max_loan_amount: number
  recommended_interest_rate: number
  risk_score: number
  risk_level: 'high' | 'medium' | 'low'
  limiting_constraint: string
  explanations: Record<string, unknown>
}

export interface ResearchResult {
  company_id: string
  data_type: string
  source_url?: string
  content: Record<string, unknown>
  sentiment?: string
  retrieved_at: string
}

export interface CAMDocument {
  application_id: string
  company_name: string
  generated_date: string
  version: number
  sections: Record<string, string>
}
