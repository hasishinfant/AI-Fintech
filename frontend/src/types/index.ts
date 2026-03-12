/**
 * Core type definitions for Intelli-Credit frontend
 */

export interface Application {
  application_id: string
  company_id: string
  loan_amount_requested: number
  loan_purpose: string
  submitted_date: string
  status: 'pending' | 'processing' | 'completed' | 'rejected'
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
  character: number
  capacity: number
  capital: number
  collateral: number
  conditions: number
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
  risk_score: RiskScore
  limiting_constraint: string
}
