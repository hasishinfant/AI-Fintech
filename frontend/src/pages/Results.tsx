import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../services/api';
import { RiskScoreCard } from '../components/RiskScoreCard';
import { ResearchInsights } from '../components/ResearchInsights';
import { CAMPreview } from '../components/CAMPreview';
import { FiveCsScorecard } from './Analysis/FiveCsScorecard';
import { Application, CreditAssessment, ResearchResult, CAMDocument } from '../types';

export const Results: React.FC = () => {
  const { applicationId } = useParams<{ applicationId: string }>();
  const navigate = useNavigate();

  const { data: application, isLoading: appLoading } = useQuery<Application>({
    queryKey: ['application', applicationId],
    queryFn: async () => {
      const response = await apiClient.get<Application>(`/applications/${applicationId}`);
      return response.data;
    },
  });

  const { data: assessment } = useQuery<CreditAssessment>({
    queryKey: ['credit-assessment', applicationId],
    queryFn: async () => {
      const response = await apiClient.get<CreditAssessment>(`/applications/${applicationId}/credit-assessment`);
      return response.data;
    },
    enabled: !!applicationId,
  });

  const { data: research } = useQuery<ResearchResult[]>({
    queryKey: ['research', applicationId],
    queryFn: async () => {
      const response = await apiClient.get<ResearchResult[]>(`/applications/${applicationId}/research`);
      return response.data;
    },
    enabled: !!applicationId,
  });

  const { data: cam } = useQuery<CAMDocument>({
    queryKey: ['cam', applicationId],
    queryFn: async () => {
      const response = await apiClient.get<CAMDocument>(`/applications/${applicationId}/cam`);
      return response.data;
    },
    enabled: !!applicationId,
  });

  if (appLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-primary-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">Loading analysis results...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-gradient-to-r from-secondary-500 to-secondary-600 text-white shadow-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <button 
                onClick={() => navigate('/dashboard')}
                className="text-white hover:text-primary-300 transition-colors"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                </svg>
              </button>
              <div>
                <h1 className="text-3xl font-bold">Credit Analysis Results</h1>
                <p className="text-gray-200 mt-1">{application?.company_name}</p>
              </div>
            </div>
            <div className="flex space-x-3">
              <button className="bg-white text-secondary-500 px-6 py-2 rounded-lg font-semibold hover:bg-gray-100 transition-all">
                Export Report
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="space-y-8">
          {/* Risk Score Card */}
          {assessment && (
            <div className="card">
              <RiskScoreCard
                riskScore={assessment.risk_score}
                riskLevel={assessment.risk_level}
                maxLoanAmount={assessment.max_loan_amount}
              />
            </div>
          )}

          {/* Five Cs Analysis */}
          {applicationId && (
            <div className="card">
              <h2 className="text-2xl font-bold text-secondary-500 mb-6">Five Cs Credit Assessment</h2>
              <FiveCsScorecard applicationId={applicationId} />
            </div>
          )}

          {/* Research Insights */}
          {research && research.length > 0 && (
            <div className="card">
              <h2 className="text-2xl font-bold text-secondary-500 mb-6">Research Insights</h2>
              <ResearchInsights research={research} />
            </div>
          )}

          {/* CAM Preview */}
          {cam && applicationId && (
            <div className="card">
              <h2 className="text-2xl font-bold text-secondary-500 mb-6">Credit Appraisal Memo</h2>
              <CAMPreview cam={cam} applicationId={applicationId} />
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
