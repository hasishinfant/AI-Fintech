import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../../api/client';
import { LoanRecommendation } from '../../types';

interface RecommendationPanelProps {
  applicationId: string;
}

export const RecommendationPanel: React.FC<RecommendationPanelProps> = ({ applicationId }) => {
  const { data: recommendation, isLoading } = useQuery<LoanRecommendation>({
    queryKey: ['recommendation', applicationId],
    queryFn: async () => {
      const response = await apiClient.get<LoanRecommendation>(`/applications/${applicationId}/recommendation`);
      return response.data;
    },
  });

  if (isLoading) return <div className="p-4">Loading recommendation...</div>;
  if (!recommendation) return <div className="p-4">No recommendation available</div>;

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold">Loan Recommendation</h2>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white p-6 rounded shadow">
          <p className="text-gray-600 mb-2">Maximum Loan Amount</p>
          <p className="text-3xl font-bold text-blue-600">₹{(recommendation.max_loan_amount / 100000).toFixed(1)}L</p>
        </div>

        <div className="bg-white p-6 rounded shadow">
          <p className="text-gray-600 mb-2">Recommended Interest Rate</p>
          <p className="text-3xl font-bold text-green-600">{recommendation.recommended_interest_rate.toFixed(2)}%</p>
        </div>

        <div className="bg-white p-6 rounded shadow">
          <p className="text-gray-600 mb-2">Risk Level</p>
          <p className={`text-2xl font-bold ${
            recommendation.risk_level === 'low' ? 'text-green-600' :
            recommendation.risk_level === 'medium' ? 'text-yellow-600' :
            'text-red-600'
          }`}>
            {recommendation.risk_level.toUpperCase()}
          </p>
        </div>
      </div>

      <div className="bg-white p-6 rounded shadow">
        <h3 className="font-bold text-lg mb-4">Limiting Constraint</h3>
        <p className="text-gray-700">{recommendation.limiting_constraint || 'No constraints identified'}</p>
      </div>

      <div className="bg-white p-6 rounded shadow">
        <h3 className="font-bold text-lg mb-4">Explanation</h3>
        <div className="space-y-2">
          {recommendation.explanations && Object.entries(recommendation.explanations).map(([key, value]) => (
            <div key={key} className="border-l-4 border-blue-500 pl-4">
              <p className="font-semibold capitalize">{key.replace(/_/g, ' ')}</p>
              <p className="text-gray-600">{typeof value === 'string' ? value : JSON.stringify(value)}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
