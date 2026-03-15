import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { QueryClientProvider, QueryClient } from '@tanstack/react-query';
import { Navbar } from './components/Navbar';
import { Footer } from './components/Footer';
import { LandingPage } from './pages/LandingPage';
import { Dashboard } from './pages/Dashboard';
import { UploadDocuments } from './pages/UploadDocuments';
import { Results } from './pages/Results';
import { ApplicationList } from './pages/Applications/ApplicationList';
import { ApplicationDetail } from './pages/Applications/ApplicationDetail';
import { ResearchPanel } from './pages/Analysis/ResearchPanel';
import { FiveCsScorecard } from './pages/Analysis/FiveCsScorecard';
import { RecommendationPanel } from './pages/Recommendation/RecommendationPanel';
import { CAMPreview } from './pages/Recommendation/CAMPreview';
import { Login } from './pages/Login';
import { apiClient } from './services/api';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const token = apiClient.getToken();
  const location = useLocation();

  if (!token) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return <>{children}</>;
};

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <div className="min-h-screen flex flex-col">
          <Navbar />
          
          <main className="flex-grow">
            <Routes>
              <Route path="/" element={<LandingPage />} />
              <Route path="/login" element={<Login />} />
              
              <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
              <Route path="/upload" element={<ProtectedRoute><UploadDocuments /></ProtectedRoute>} />
              <Route path="/results/:applicationId" element={<ProtectedRoute><Results /></ProtectedRoute>} />
              <Route path="/applications" element={<ProtectedRoute><ApplicationList /></ProtectedRoute>} />
              <Route path="/applications/:applicationId" element={<ProtectedRoute><ApplicationDetail /></ProtectedRoute>} />
              <Route path="/applications/:applicationId/research" element={<ProtectedRoute><ResearchPanel applicationId={''} /></ProtectedRoute>} />
              <Route path="/applications/:applicationId/analysis" element={<ProtectedRoute><FiveCsScorecard applicationId={''} /></ProtectedRoute>} />
              <Route path="/applications/:applicationId/recommendation" element={<ProtectedRoute><RecommendationPanel applicationId={''} /></ProtectedRoute>} />
              <Route path="/applications/:applicationId/cam" element={<ProtectedRoute><CAMPreview applicationId={''} /></ProtectedRoute>} />
              
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </main>

          <Footer />
        </div>
      </Router>
    </QueryClientProvider>
  );
}

export default App;
