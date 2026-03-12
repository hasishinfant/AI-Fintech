import React, { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { apiClient } from '../../api/client';

interface CAMPreviewProps {
  applicationId: string;
}

export const CAMPreview: React.FC<CAMPreviewProps> = ({ applicationId }) => {
  const [activeSection, setActiveSection] = useState('executive_summary');

  const { data: cam, isLoading } = useQuery({
    queryKey: ['cam', applicationId],
    queryFn: async () => {
      const response = await apiClient.get(`/applications/${applicationId}/cam`);
      return response.data;
    },
  });

  const generateMutation = useMutation({
    mutationFn: async () => {
      return await apiClient.post(`/applications/${applicationId}/cam/generate`);
    },
  });

  const exportWordMutation = useMutation({
    mutationFn: async () => {
      const response = await apiClient.get(`/applications/${applicationId}/cam/export/word`);
      return response.data;
    },
  });

  const exportPdfMutation = useMutation({
    mutationFn: async () => {
      const response = await apiClient.get(`/applications/${applicationId}/cam/export/pdf`);
      return response.data;
    },
  });

  if (isLoading) return <div className="p-4">Loading CAM...</div>;

  const sections = cam?.sections ? Object.keys(cam.sections) : [];

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold">Credit Appraisal Memo</h2>

      {!cam && (
        <button
          onClick={() => generateMutation.mutate()}
          disabled={generateMutation.isPending}
          className="px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-gray-400"
        >
          {generateMutation.isPending ? 'Generating...' : 'Generate CAM'}
        </button>
      )}

      {cam && (
        <>
          <div className="flex gap-2 mb-4">
            <button
              onClick={() => exportWordMutation.mutate()}
              disabled={exportWordMutation.isPending}
              className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:bg-gray-400"
            >
              {exportWordMutation.isPending ? 'Exporting...' : 'Export to Word'}
            </button>
            <button
              onClick={() => exportPdfMutation.mutate()}
              disabled={exportPdfMutation.isPending}
              className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 disabled:bg-gray-400"
            >
              {exportPdfMutation.isPending ? 'Exporting...' : 'Export to PDF'}
            </button>
          </div>

          <div className="bg-white p-6 rounded shadow">
            <div className="flex gap-2 mb-4 border-b">
              {sections.map((section) => (
                <button
                  key={section}
                  onClick={() => setActiveSection(section)}
                  className={`px-4 py-2 ${
                    activeSection === section
                      ? 'border-b-2 border-blue-600 text-blue-600'
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  {section.replace(/_/g, ' ').toUpperCase()}
                </button>
              ))}
            </div>

            <div className="prose max-w-none">
              <p className="text-gray-700 whitespace-pre-wrap">
                {cam.sections[activeSection] || 'No content available'}
              </p>
            </div>
          </div>

          <div className="bg-gray-50 p-4 rounded text-sm text-gray-600">
            <p>Generated: {new Date(cam.generated_date).toLocaleString()}</p>
            <p>Version: {cam.version}</p>
          </div>
        </>
      )}
    </div>
  );
};
