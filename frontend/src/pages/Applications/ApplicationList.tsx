import React, { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../../api/client';
import { Application } from '../../types';

export const ApplicationList: React.FC = () => {
  const [applications, setApplications] = useState<Application[]>([]);

  const { data, isLoading, error } = useQuery({
    queryKey: ['applications'],
    queryFn: async () => {
      const response = await apiClient.get<Application[]>('/applications');
      return response.data;
    },
  });

  useEffect(() => {
    if (data) {
      setApplications(data);
    }
  }, [data]);

  if (isLoading) return <div className="p-4">Loading applications...</div>;
  if (error) return <div className="p-4 text-red-600">Error loading applications: {error.message}</div>;

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-6">Loan Applications</h1>
      <div className="overflow-x-auto">
        <table className="w-full border-collapse border border-gray-300">
          <thead className="bg-gray-100">
            <tr>
              <th className="border p-2 text-left">Application ID</th>
              <th className="border p-2 text-left">Company</th>
              <th className="border p-2 text-left">Loan Amount</th>
              <th className="border p-2 text-left">Purpose</th>
              <th className="border p-2 text-left">Status</th>
              <th className="border p-2 text-left">Submitted</th>
              <th className="border p-2 text-left">Actions</th>
            </tr>
          </thead>
          <tbody>
            {applications.map((app) => (
              <tr key={app.application_id} className="hover:bg-gray-50">
                <td className="border p-2">{app.application_id.slice(0, 8)}</td>
                <td className="border p-2">{app.company_name || 'N/A'}</td>
                <td className="border p-2">₹{app.loan_amount_requested.toLocaleString()}</td>
                <td className="border p-2">{app.loan_purpose}</td>
                <td className="border p-2">
                  <span className={`px-2 py-1 rounded text-sm ${
                    app.status === 'completed' ? 'bg-green-100 text-green-800' :
                    app.status === 'processing' ? 'bg-blue-100 text-blue-800' :
                    'bg-gray-100 text-gray-800'
                  }`}>
                    {app.status}
                  </span>
                </td>
                <td className="border p-2">{new Date(app.submitted_date).toLocaleDateString()}</td>
                <td className="border p-2">
                  <a href={`/applications/${app.application_id}`} className="text-blue-600 hover:underline">
                    View
                  </a>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
