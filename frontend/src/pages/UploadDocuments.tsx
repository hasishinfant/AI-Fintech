import React, { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { apiClient } from '../services/api';
import { UploadPanel } from '../components/UploadPanel';

export const UploadDocuments: React.FC = () => {
  const navigate = useNavigate();
  const [companyName, setCompanyName] = useState('');
  const [applicationId, setApplicationId] = useState<string | null>(null);

  const createApplicationMutation = useMutation({
    mutationFn: async (name: string) => {
      const response = await apiClient.post('/applications', { company_name: name });
      return response.data;
    },
    onSuccess: (data) => {
      setApplicationId(data.id);
    },
  });

  const handleCreateApplication = () => {
    if (companyName.trim()) {
      createApplicationMutation.mutate(companyName);
    }
  };

  const handleUploadComplete = () => {
    if (applicationId) {
      navigate(`/results/${applicationId}`);
    }
  };

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">New Credit Application</h1>

      {!applicationId ? (
        <div className="bg-white p-6 rounded shadow">
          <h3 className="font-bold text-lg mb-4">Company Information</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Company Name
              </label>
              <input
                type="text"
                value={companyName}
                onChange={(e) => setCompanyName(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
                placeholder="Enter company name"
              />
            </div>
            <button
              onClick={handleCreateApplication}
              disabled={!companyName.trim() || createApplicationMutation.isPending}
              className="px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-gray-400"
            >
              {createApplicationMutation.isPending ? 'Creating...' : 'Create Application'}
            </button>
          </div>
        </div>
      ) : (
        <div className="space-y-6">
          <div className="bg-green-50 p-4 rounded">
            <p className="text-green-800">
              Application created successfully for <strong>{companyName}</strong>
            </p>
          </div>
          <UploadPanel 
            applicationId={applicationId} 
            onUploadComplete={handleUploadComplete}
          />
        </div>
      )}
    </div>
  );
};
