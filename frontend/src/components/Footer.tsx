import React from 'react';
import { Link } from 'react-router-dom';

export const Footer: React.FC = () => {
  return (
    <footer className="bg-secondary-700 text-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid md:grid-cols-4 gap-8">
          <div>
            <div className="flex items-center space-x-3 mb-4">
              <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-primary-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-xl">IC</span>
              </div>
              <span className="text-xl font-bold">Intelli-Credit</span>
            </div>
            <p className="text-gray-300 text-sm">
              AI-powered credit decisioning for modern financial institutions
            </p>
          </div>
          
          <div>
            <h4 className="font-semibold mb-4">Product</h4>
            <ul className="space-y-2 text-sm">
              <li><Link to="/features" className="text-gray-300 hover:text-primary-500 transition-colors">Features</Link></li>
              <li><Link to="/pricing" className="text-gray-300 hover:text-primary-500 transition-colors">Pricing</Link></li>
              <li><Link to="/demo" className="text-gray-300 hover:text-primary-500 transition-colors">Request Demo</Link></li>
            </ul>
          </div>
          
          <div>
            <h4 className="font-semibold mb-4">Company</h4>
            <ul className="space-y-2 text-sm">
              <li><Link to="/about" className="text-gray-300 hover:text-primary-500 transition-colors">About Us</Link></li>
              <li><Link to="/contact" className="text-gray-300 hover:text-primary-500 transition-colors">Contact</Link></li>
              <li><Link to="/careers" className="text-gray-300 hover:text-primary-500 transition-colors">Careers</Link></li>
            </ul>
          </div>
          
          <div>
            <h4 className="font-semibold mb-4">Legal</h4>
            <ul className="space-y-2 text-sm">
              <li><Link to="/privacy" className="text-gray-300 hover:text-primary-500 transition-colors">Privacy Policy</Link></li>
              <li><Link to="/terms" className="text-gray-300 hover:text-primary-500 transition-colors">Terms of Service</Link></li>
              <li><Link to="/security" className="text-gray-300 hover:text-primary-500 transition-colors">Security</Link></li>
            </ul>
          </div>
        </div>
        
        <div className="border-t border-secondary-600 mt-8 pt-8 text-center text-sm text-gray-300">
          <p>&copy; 2024 Intelli-Credit. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
};
