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
  const getRiskColor = (level: string) => {
    switch (level.toLowerCase()) {
      case 'low':
        return { bg: 'bg-green-500', text: 'text-green-600', badge: 'badge-success' };
      case 'medium':
        return { bg: 'bg-yellow-500', text: 'text-yellow-600', badge: 'badge-warning' };
      case 'high':
        return { bg: 'bg-red-500', text: 'text-red-600', badge: 'badge-danger' };
      default:
        return { bg: 'bg-gray-500', text: 'text-gray-600', badge: 'badge-info' };
    }
  };

  const colors = getRiskColor(riskLevel);

  return (
    <div className="grid md:grid-cols-3 gap-6">
      {/* Risk Score */}
      <div className="bg-gradient-to-br from-primary-50 to-primary-100 rounded-xl p-6 border border-primary-200">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-700">Risk Score</h3>
          <div className="w-10 h-10 bg-primary-500 rounded-lg flex items-center justify-center">
            <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
          </div>
        </div>
        <div className="flex items-end space-x-2">
          <span className="text-5xl font-bold text-secondary-500">{riskScore.toFixed(0)}</span>
          <span className="text-2xl text-gray-600 mb-2">/100</span>
        </div>
        <div className="mt-4 w-full bg-gray-200 rounded-full h-3">
          <div 
            className={`${colors.bg} h-3 rounded-full transition-all duration-500`}
            style={{ width: `${riskScore}%` }}
          ></div>
        </div>
      </div>

      {/* Risk Level */}
      <div className="bg-gradient-to-br from-secondary-50 to-secondary-100 rounded-xl p-6 border border-secondary-200">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-700">Risk Level</h3>
          <div className="w-10 h-10 bg-secondary-500 rounded-lg flex items-center justify-center">
            <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
        </div>
        <div className="flex items-center space-x-3">
          <span className={`text-4xl font-bold ${colors.text} capitalize`}>
            {riskLevel}
          </span>
          <span className={`${colors.badge} text-lg`}>
            {riskLevel === 'low' ? '✓' : riskLevel === 'medium' ? '!' : '⚠'}
          </span>
        </div>
        <p className="mt-4 text-sm text-gray-600">
          {riskLevel === 'low' && 'Excellent creditworthiness with minimal risk'}
          {riskLevel === 'medium' && 'Moderate risk with acceptable credit profile'}
          {riskLevel === 'high' && 'Elevated risk requiring careful consideration'}
        </p>
      </div>

      {/* Max Loan Amount */}
      <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-xl p-6 border border-green-200">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-700">Max Loan Amount</h3>
          <div className="w-10 h-10 bg-green-500 rounded-lg flex items-center justify-center">
            <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
        </div>
        <div className="flex items-baseline space-x-2">
          <span className="text-4xl font-bold text-secondary-500">
            ₹{(maxLoanAmount / 10000000).toFixed(2)}
          </span>
          <span className="text-xl text-gray-600">Cr</span>
        </div>
        <p className="mt-4 text-sm text-gray-600">
          Recommended maximum lending amount based on analysis
        </p>
      </div>
    </div>
  );
};
