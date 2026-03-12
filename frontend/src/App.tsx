import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClientProvider, QueryClient } from '@tanstack/react-query';
import { ApplicationList } from './pages/Applications/ApplicationList';
import { ApplicationDetail } from './pages/Applications/ApplicationDetail';
import { ResearchPanel } from './pages/Analysis/ResearchPanel';
import { FiveCsScorecard } from './pages/Analysis/FiveCsScorecard';
import { RecommendationPanel } from './pages/Recommendation/RecommendationPanel';
import { CAMPreview } from './pages/Recommendation/CAMPreview';

const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <div className="min-h-screen bg-gray-50">
          <nav className="bg-white shadow">
            <div className="max-w-7xl mx-auto px-4 py-4">
              <h1 className="text-2xl font-bold text-blue-600">Intelli-Credit</h1>
            </div>
          </nav>

          <main className="max-w-7xl mx-auto">
            <Routes>
              <Route path="/" element={<ApplicationList />} />
              <Route path="/applications/:applicationId" element={<ApplicationDetail />} />
              <Route path="/applications/:applicationId/research" element={<ResearchPanel applicationId={''} />} />
              <Route path="/applications/:applicationId/analysis" element={<FiveCsScorecard applicationId={''} />} />
              <Route path="/applications/:applicationId/recommendation" element={<RecommendationPanel applicationId={''} />} />
              <Route path="/applications/:applicationId/cam" element={<CAMPreview applicationId={''} />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </main>
        </div>
      </Router>
    </QueryClientProvider>
  );
}

export default App;
