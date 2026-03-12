import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../../api/client';

interface FiveCsScores {
  character_score: number;
  capacity_score: number;
  capital_score: number;
  collateral_score: number;
  conditions_score: number;
}

interface FiveCsScorecardProps {
  applicationId: string;
}

export const FiveCsScorecard: React.FC<FiveCsScorecardProps> = ({ applicationId }) => {
  const { data: assessment, isLoading } = useQuery({
    queryKey: ['credit-assessment', applicationId],
    queryFn: async () => {
      const response = await apiClient.get(`/applications/${applicationId}/credit-assessment`);
      return response.data;
    },
  });

  if (isLoading) return <div className="p-4">Loading assessment...</div>;
  if (!assessment) return <div className="p-4">No assessment available</div>;

  const scores = assessment.five_cs_scores as FiveCsScores;
  const categories = [
    { name: 'Character', score: scores.character_score },
    { name: 'Capacity', score: scores.capacity_score },
    { name: 'Capital', score: scores.capital_score },
    { name: 'Collateral', score: scores.collateral_score },
    { name: 'Conditions', score: scores.conditions_score },
  ];

  const getScoreColor = (score: number) => {
    if (score >= 70) return 'bg-green-500';
    if (score >= 50) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold">Five Cs Analysis</h2>

      <div className="bg-white p-6 rounded shadow">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {categories.map((cat) => (
            <div key={cat.name} className="flex flex-col items-center">
              <div className="relative w-32 h-32 rounded-full border-8 border-gray-200 flex items-center justify-center">
                <div className={`absolute inset-0 rounded-full ${getScoreColor(cat.score)} opacity-20`}></div>
                <div className="text-center z-10">
                  <p className="text-3xl font-bold">{cat.score.toFixed(1)}</p>
                  <p className="text-sm text-gray-600">/100</p>
                </div>
              </div>
              <p className="mt-4 font-bold text-lg">{cat.name}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="bg-white p-6 rounded shadow">
        <h3 className="font-bold text-lg mb-4">Overall Risk Assessment</h3>
        <div className="grid grid-cols-3 gap-4">
          <div className="text-center">
            <p className="text-gray-600">Risk Score</p>
            <p className="text-3xl font-bold">{assessment.risk_score.toFixed(1)}</p>
          </div>
          <div className="text-center">
            <p className="text-gray-600">Risk Level</p>
            <p className={`text-2xl font-bold ${
              assessment.risk_level === 'low' ? 'text-green-600' :
              assessment.risk_level === 'medium' ? 'text-yellow-600' :
              'text-red-600'
            }`}>
              {assessment.risk_level.toUpperCase()}
            </p>
          </div>
          <div className="text-center">
            <p className="text-gray-600">Max Loan Amount</p>
            <p className="text-2xl font-bold">₹{(assessment.max_loan_amount / 100000).toFixed(1)}L</p>
          </div>
        </div>
      </div>
    </div>
  );
};
