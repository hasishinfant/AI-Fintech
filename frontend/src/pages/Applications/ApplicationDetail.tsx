import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import { useQuery, useMutation } from '@tanstack/react-query';
import { apiClient } from '../../api/client';
import { Application } from '../../types';

export const ApplicationDetail: React.FC = () => {
  const { applicationId } = useParams<{ applicationId: string }>();
  const [activeTab, setActiveTab] = useState('overview');

  const { data: application, isLoading } = useQuery<Application>({
    queryKey: ['application', applicationId],
    queryFn: async () => {
      const response = await apiClient.get<Application>(`/applications/${applicationId}`);
      return response.data;
    },
  });

  const processMutation = useMutation({
    mutationFn: async () => {
      return await apiClient.post(`/applications/${applicationId}/process`);
    },
  });

  if (isLoading) return <div className="p-4">Loading application...</div>;
  if (!application) return <div className="p-4">Application not found</div>;

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2">Application Details</h1>
        <p className="text-gray-600">ID: {applicationId}</p>
      </div>

      <div className="mb-6 flex gap-2">
        <button
          onClick={() => setActiveTab('overview')}
          className={`px-4 py-2 rounded ${activeTab === 'overview' ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}
        >
          Overview
        </button>
        <button
          onClick={() => setActiveTab('documents')}
          className={`px-4 py-2 rounded ${activeTab === 'documents' ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}
        >
          Documents
        </button>
        <button
          onClick={() => setActiveTab('analysis')}
          className={`px-4 py-2 rounded ${activeTab === 'analysis' ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}
        >
          Analysis
        </button>
      </div>

      {activeTab === 'overview' && (
        <div className="bg-white p-6 rounded shadow">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-gray-600">Loan Amount Requested</label>
              <p className="text-2xl font-bold">₹{application.loan_amount_requested.toLocaleString()}</p>
            </div>
            <div>
              <label className="text-gray-600">Purpose</label>
              <p className="text-lg">{application.loan_purpose}</p>
            </div>
            <div>
              <label className="text-gray-600">Status</label>
              <p className="text-lg">{application.status}</p>
            </div>
            <div>
              <label className="text-gray-600">Submitted Date</label>
              <p className="text-lg">{new Date(application.submitted_date).toLocaleDateString()}</p>
            </div>
          </div>

          <button
            onClick={() => processMutation.mutate()}
            disabled={processMutation.isPending}
            className="mt-6 px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-gray-400"
          >
            {processMutation.isPending ? 'Processing...' : 'Start Processing'}
          </button>
        </div>
      )}

      {activeTab === 'documents' && (
        <div className="bg-white p-6 rounded shadow">
          <h2 className="text-xl font-bold mb-4">Upload Documents</h2>
          <div className="border-2 border-dashed border-gray-300 rounded p-8 text-center">
            <p className="text-gray-600">Drag and drop documents here or click to upload</p>
            <input type="file" multiple className="mt-4" />
          </div>
        </div>
      )}

      {activeTab === 'analysis' && (
        <div className="bg-white p-6 rounded shadow">
          <h2 className="text-xl font-bold mb-4">Analysis Results</h2>
          <p className="text-gray-600">Analysis will appear here once processing is complete</p>
        </div>
      )}
    </div>
  );
};
