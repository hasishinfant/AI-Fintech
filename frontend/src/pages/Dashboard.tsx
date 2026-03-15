import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../services/api';
import { Link } from 'react-router-dom';
import { Application } from '../types';

export const Dashboard: React.FC = () => {
  const { data: applications, isLoading } = useQuery<Application[]>({
    queryKey: ['applications'],
    queryFn: async () => {
      const response = await apiClient.get<Application[]>('/applications');
      return response.data;
    },
  });

  const stats = [
    { 
      label: 'Total Applications', 
      value: applications?.length || 0, 
      change: '+12%', 
      color: 'primary' 
    },
    { 
      label: 'Approved This Month', 
      value: applications?.filter((a: Application) => a.status === 'approved').length || 0, 
      change: '+8%', 
      color: 'green' 
    },
    { 
      label: 'Pending Review', 
      value: applications?.filter((a: Application) => a.status === 'pending').length || 0, 
      change: '+3%', 
      color: 'blue' 
    },
    { 
      label: 'Processing Time', 
      value: '4.2m', 
      change: '-15%', 
      color: 'secondary' 
    },
  ];

  const getStatusBadge = (status: string) => {
    const badges = {
      approved: 'badge-success',
      rejected: 'badge-danger',
      pending: 'badge-warning',
      processing: 'badge-info',
    };
    return badges[status as keyof typeof badges] || 'badge-info';
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-primary-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-secondary-500">Dashboard</h1>
              <p className="text-gray-600 mt-1">Welcome back! Here's your credit portfolio overview</p>
            </div>
            <Link to="/upload" className="btn-primary">
              <svg className="w-5 h-5 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              New Application
            </Link>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Grid */}
        <div className="grid md:grid-cols-4 gap-6 mb-8">
          {stats.map((stat, idx) => (
            <div key={idx} className="card">
              <div className="flex justify-between items-start mb-2">
                <span className="text-gray-600 text-sm">{stat.label}</span>
                <span className={`text-xs font-semibold ${stat.change.startsWith('+') ? 'text-green-600' : 'text-red-600'}`}>
                  {stat.change}
                </span>
              </div>
              <div className="text-3xl font-bold text-secondary-500">{stat.value}</div>
            </div>
          ))}
        </div>

        {/* Quick Actions */}
        <div className="grid md:grid-cols-3 gap-6 mb-8">
          <Link to="/upload" className="card hover:scale-105 transition-transform cursor-pointer">
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 bg-gradient-to-br from-primary-500 to-primary-600 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
              </div>
              <div>
                <h3 className="font-semibold text-secondary-500">Upload Documents</h3>
                <p className="text-sm text-gray-600">Start new application</p>
              </div>
            </div>
          </Link>

          <Link to="/applications" className="card hover:scale-105 transition-transform cursor-pointer">
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 bg-gradient-to-br from-secondary-500 to-secondary-600 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <div>
                <h3 className="font-semibold text-secondary-500">View Applications</h3>
                <p className="text-sm text-gray-600">Browse all submissions</p>
              </div>
            </div>
          </Link>

          <div className="card hover:scale-105 transition-transform cursor-pointer">
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 bg-gradient-to-br from-green-500 to-green-600 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <div>
                <h3 className="font-semibold text-secondary-500">Analytics</h3>
                <p className="text-sm text-gray-600">View insights</p>
              </div>
            </div>
          </div>
        </div>

        {/* Recent Applications */}
        <div className="card">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold text-secondary-500">Recent Applications</h2>
            <Link to="/applications" className="text-primary-500 hover:text-primary-600 font-medium">
              View All →
            </Link>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-3 px-4 text-gray-600 font-semibold">Company</th>
                  <th className="text-left py-3 px-4 text-gray-600 font-semibold">Status</th>
                  <th className="text-left py-3 px-4 text-gray-600 font-semibold">Risk Level</th>
                  <th className="text-left py-3 px-4 text-gray-600 font-semibold">Date</th>
                  <th className="text-left py-3 px-4 text-gray-600 font-semibold">Actions</th>
                </tr>
              </thead>
              <tbody>
                {applications?.map((app: Application) => (
                  <tr key={app.application_id} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="py-4 px-4">
                      <div className="font-semibold text-secondary-500">{app.company_name}</div>
                    </td>
                    <td className="py-4 px-4">
                      <span className={`${getStatusBadge(app.status)} capitalize`}>
                        {app.status}
                      </span>
                    </td>
                    <td className="py-4 px-4">
                      {app.risk_level ? (
                        <span className="font-semibold text-secondary-500">{app.risk_level}</span>
                      ) : (
                        <span className="text-gray-400">-</span>
                      )}
                    </td>
                    <td className="py-4 px-4 text-gray-600">
                      {new Date(app.created_at).toLocaleDateString()}
                    </td>
                    <td className="py-4 px-4">
                      <Link 
                        to={`/results/${app.application_id}`}
                        className="text-primary-500 hover:text-primary-600 font-medium"
                      >
                        View Details →
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};
