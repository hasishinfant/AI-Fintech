import React from 'react';

interface ServiceCardProps {
  icon: React.ReactNode;
  title: string;
  description: string;
  color: 'primary' | 'secondary' | 'green' | 'blue';
}

export const ServiceCard: React.FC<ServiceCardProps> = ({ icon, title, description, color }) => {
  const colorClasses = {
    primary: 'from-primary-500 to-primary-600',
    secondary: 'from-secondary-500 to-secondary-600',
    green: 'from-green-500 to-green-600',
    blue: 'from-blue-500 to-blue-600',
  };

  return (
    <div className="relative group">
      <div className={`absolute inset-0 bg-gradient-to-br ${colorClasses[color]} rounded-xl opacity-0 group-hover:opacity-10 transition-opacity duration-300`}></div>
      <div className="card relative">
        <div className={`w-16 h-16 bg-gradient-to-br ${colorClasses[color]} rounded-xl flex items-center justify-center mb-4`}>
          {icon}
        </div>
        <h3 className="text-2xl font-bold text-secondary-500 mb-3">{title}</h3>
        <p className="text-gray-600 leading-relaxed">{description}</p>
      </div>
    </div>
  );
};
