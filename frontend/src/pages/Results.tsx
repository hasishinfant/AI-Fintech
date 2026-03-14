import React from 'react';
import { useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../services/api';
import { RiskScoreCard } from '../components/RiskScoreCard';
import { ResearchInsights } from '../components/ResearchInsights';
import { CAMPreview } from '../components/CAMPreview';
import { FiveCsScorecard } from './Analysis/FiveCsScorecard';

export const Results: React.FC = () => {
  const { applicationId } = useParams<{ applicationId: string }>();

  const { data: application, isLoading: appLoading } = useQuery({
    queryKey: ['application', applicationId],
    queryFn: async () => {
      const response = await apiClient.get(`/applications/${applicationId}`);
      return response.data;
    },
  });

  const { data: assessment, isLoading: assessmentLoading } = useQuery({
    queryKey: ['credit-assessment', applicationId],
    queryFn: async () => {
      const response = await apiClient.get(`/applications/${applicationId}/credit-assessment`);
      return response.data;
    },
    enabled: !!applicationId,
  });

  const { data: research, isLoading: researchLoading } = useQuery({
    queryKey: ['research', applicationId],
    queryFn: async () => {
      const response = await apiClient.get(`/applications/${applicationId}/research`);
      return response.data;
    },
    enabled: !!applicationId,
  });

  const { data: cam, isLoading: camLoading } = useQuery({
    queryKey: ['cam', applicationId],
    queryFn: async () => {
      const response = await apiClient.get(`/applications/${applicationId}/cam`);
      return response.data;
    },
    enabled: !!applicationId,
  });

  if (appLoading) return <div className="p-8">Loading application...</div>;

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-6">
        Credit Analysis: {application?.company_name}
      </h1>

      <div className="space-y-8">
        {/* Risk Score Card */}
        {assessment && (
          <RiskScoreCard
            riskScore={assessment.risk_score}
            riskLevel={assessment.risk_level}
            maxLoanAmount={assessment.max_loan_amount}
          />
        )}

        {/* Five Cs Analysis */}
        {applicationId && <FiveCsScorecard applicationId={applicationId} />}

        {/* Research Insights */}
        {research && research.length > 0 && (
          <ResearchInsights research={research} />
        )}

        {/* CAM Preview */}
        {cam && applicationId && (
          <div>
            <h2 className="text-2xl font-bold mb-4">Credit Appraisal Memo</h2>
            <CAMPreview cam={cam} applicationId={applicationId} />
          </div>
        )}
      </div>
    </div>
  );
};
