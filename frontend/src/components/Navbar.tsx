import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { apiClient } from '../services/api';

export const Navbar: React.FC = () => {
  const navigate = useNavigate();
  const token = apiClient.getToken();

  const handleLogout = () => {
    apiClient.clearToken();
    navigate('/');
    window.location.reload(); // Refresh to clear any local state in queries
  };

  return (
    <nav className="bg-white shadow-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <Link to="/" className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-xl">IC</span>
            </div>
            <span className="text-2xl font-bold text-secondary-500">Intelli-Credit</span>
          </Link>
          
          <div className="hidden md:flex items-center space-x-8">
            <Link to="/" className="text-gray-700 hover:text-primary-500 font-medium transition-colors">
              Home
            </Link>
            <Link to="/dashboard" className="text-gray-700 hover:text-primary-500 font-medium transition-colors">
              Dashboard
            </Link>
            <Link to="/applications" className="text-gray-700 hover:text-primary-500 font-medium transition-colors">
              Applications
            </Link>
            {token ? (
              <>
                <Link to="/upload" className="btn-primary">
                  Upload Documents
                </Link>
                <button 
                  onClick={handleLogout}
                  className="text-gray-700 hover:text-red-500 font-medium transition-colors"
                >
                  Logout
                </button>
              </>
            ) : (
              <Link to="/login" className="btn-primary">
                Login
              </Link>
            )}
          </div>
          
          <button className="md:hidden">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
        </div>
      </div>
    </nav>
  );
};
