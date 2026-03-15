import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../../api/client';
import { ResearchResult } from '../../types';

interface ResearchData {
  data_type: string;
  source_url?: string;
  content: Record<string, unknown>;
  sentiment?: string;
  retrieved_at: string;
}

interface ResearchPanelProps {
  applicationId: string;
}

export const ResearchPanel: React.FC<ResearchPanelProps> = ({ applicationId }) => {
  const { data: research, isLoading } = useQuery<ResearchResult[]>({
    queryKey: ['research', applicationId],
    queryFn: async () => {
      const response = await apiClient.get<ResearchResult[]>(`/applications/${applicationId}/research`);
      return response.data;
    },
  });

  if (isLoading) return <div className="p-4">Loading research data...</div>;

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold">Research & Intelligence</h2>

      {research?.map((item: ResearchData, idx: number) => (
        <div key={idx} className="bg-white p-4 rounded shadow">
          <div className="flex justify-between items-start mb-2">
            <h3 className="font-bold text-lg capitalize">{item.data_type}</h3>
            {item.sentiment && (
              <span className={`px-2 py-1 rounded text-sm ${
                item.sentiment === 'positive' ? 'bg-green-100 text-green-800' :
                item.sentiment === 'negative' ? 'bg-red-100 text-red-800' :
                'bg-gray-100 text-gray-800'
              }`}>
                {item.sentiment}
              </span>
            )}
          </div>
          {item.source_url && (
            <a href={item.source_url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline text-sm">
              {item.source_url}
            </a>
          )}
          <p className="text-gray-600 text-sm mt-2">
            Retrieved: {new Date(item.retrieved_at).toLocaleDateString()}
          </p>
        </div>
      ))}
    </div>
  );
};
