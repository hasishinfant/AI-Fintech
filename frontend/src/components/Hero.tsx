import React from 'react';
import { Link } from 'react-router-dom';

export const Hero: React.FC = () => {
  return (
    <div className="relative bg-gradient-to-br from-secondary-500 via-secondary-600 to-secondary-700 overflow-hidden">
      {/* Geometric background patterns */}
      <div className="absolute inset-0 opacity-10">
        <div className="absolute top-0 left-0 w-96 h-96 bg-primary-500 rounded-full filter blur-3xl"></div>
        <div className="absolute bottom-0 right-0 w-96 h-96 bg-primary-400 rounded-full filter blur-3xl"></div>
      </div>
      
      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24 md:py-32">
        <div className="grid md:grid-cols-2 gap-12 items-center">
          <div className="text-white">
            <h1 className="text-5xl md:text-6xl font-bold mb-6 leading-tight">
              Best Financing Solutions for Your Business
            </h1>
            <p className="text-xl md:text-2xl mb-8 text-gray-200">
              AI-powered credit decisioning that transforms loan processing with intelligent analysis and instant recommendations
            </p>
            <div className="flex flex-col sm:flex-row gap-4">
              <Link to="/upload" className="bg-primary-500 text-white px-8 py-4 rounded-lg font-semibold text-lg hover:bg-primary-600 transition-all duration-200 shadow-lg hover:shadow-xl text-center">
                Get Started
              </Link>
              <Link to="/dashboard" className="bg-white text-secondary-500 px-8 py-4 rounded-lg font-semibold text-lg hover:bg-gray-100 transition-all duration-200 shadow-lg hover:shadow-xl text-center">
                View Dashboard
              </Link>
            </div>
          </div>
          
          <div className="hidden md:block">
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-br from-primary-500 to-primary-600 rounded-2xl transform rotate-3"></div>
              <div className="relative bg-white rounded-2xl shadow-2xl p-8 transform -rotate-1">
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-gray-600">Risk Score</span>
                    <span className="text-3xl font-bold text-primary-500">85</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-3">
                    <div className="bg-primary-500 h-3 rounded-full" style={{ width: '85%' }}></div>
                  </div>
                  <div className="grid grid-cols-2 gap-4 pt-4">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-secondary-500">₹2.5Cr</div>
                      <div className="text-sm text-gray-600">Max Loan</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-secondary-500">8.5%</div>
                      <div className="text-sm text-gray-600">Interest Rate</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
