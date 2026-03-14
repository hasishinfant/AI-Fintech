import React from 'react';

interface RiskScoreCardProps {
  riskScore: number;
  riskLevel: string;
  maxLoanAmount: number;
}

export const RiskScoreCard: React.FC<RiskScoreCardProps> = ({ 
  riskScore, 
  riskLevel, 
  maxLoanAmount 
}) => {
  return (
    <div className="bg-white p-6 rounded shadow">
      <h3 className="font-bold text-lg mb-4">Overall Risk Assessment</h3>
      <div className="grid grid-cols-3 gap-4">
        <div className="text-center">
          <p className="text-gray-600">Risk Score</p>
          <p className="text-3xl font-bold">{riskScore.toFixed(1)}</p>
        </div>
        <div className="text-center">
          <p className="text-gray-600">Risk Level</p>
          <p className={`text-2xl font-bold ${
            riskLevel === 'low' ? 'text-green-600' :
            riskLevel === 'medium' ? 'text-yellow-600' :
            'text-red-600'
          }`}>
            {riskLevel.toUpperCase()}
          </p>
        </div>
        <div className="text-center">
          <p className="text-gray-600">Max Loan Amount</p>
          <p className="text-2xl font-bold">₹{(maxLoanAmount / 100000).toFixed(1)}L</p>
        </div>
      </div>
    </div>
  );
};
