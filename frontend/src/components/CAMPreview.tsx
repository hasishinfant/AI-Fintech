import React, { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { apiClient } from '../services/api';
import { CAMDocument } from '../types';

interface CAMPreviewProps {
  cam: CAMDocument;
  applicationId: string;
}

export const CAMPreview: React.FC<CAMPreviewProps> = ({ cam, applicationId }) => {
  const [activeSection, setActiveSection] = useState('executive_summary');

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

  const sections = cam?.sections ? Object.keys(cam.sections) : [];

  return (
    <div className="space-y-4">
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
    </div>
  );
};
