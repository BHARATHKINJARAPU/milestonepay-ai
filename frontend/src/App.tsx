import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { ProtectedRoute } from './components/auth/ProtectedRoute';
import { DashboardLayout } from './components/dashboard/DashboardLayout';
import { LandingPage } from './pages/LandingPage';
import { LoginPage } from './pages/auth/LoginPage';
import { RegisterPage } from './pages/auth/RegisterPage';
import { DashboardPage } from './pages/dashboard/DashboardPage';
import { ProjectsPage } from './pages/projects/ProjectsPage';
import { CreateProjectPage } from './pages/projects/CreateProjectPage';
import { ProjectDetailPage } from './pages/projects/ProjectDetailPage';
import { MilestoneWorkspacePage } from './pages/milestones/MilestoneWorkspacePage';
import { SubmitDeliverablePage } from './pages/submissions/SubmitDeliverablePage';
import { SubmissionDetailPage } from './pages/submissions/SubmissionDetailPage';
import { MilestonePaymentPage } from './pages/payments/MilestonePaymentPage';
import { PaymentHistoryPage } from './pages/payments/PaymentHistoryPage';
import { PaymentResultPage } from './pages/payments/PaymentResultPage';
import { NotificationsPage } from './pages/notifications/NotificationsPage';

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          {/* Public Routes */}
          <Route path="/" element={<LandingPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />

          {/* Protected Dashboard & Project Routes */}
          <Route
            element={
              <ProtectedRoute>
                <DashboardLayout />
              </ProtectedRoute>
            }
          >
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/projects" element={<ProjectsPage />} />
            <Route path="/projects/new" element={<CreateProjectPage />} />
            <Route path="/projects/:id" element={<ProjectDetailPage />} />
            <Route path="/projects/:projectId/milestones" element={<MilestoneWorkspacePage />} />
            <Route
              path="/projects/:projectId/milestones/:milestoneId/submit"
              element={<SubmitDeliverablePage />}
            />
            <Route
              path="/projects/:projectId/milestones/:milestoneId/submissions/:submissionId"
              element={<SubmissionDetailPage />}
            />
            <Route
              path="/projects/:projectId/milestones/:milestoneId/pay"
              element={<MilestonePaymentPage />}
            />
            <Route path="/payments" element={<PaymentHistoryPage />} />
            <Route path="/payments/:paymentId/result" element={<PaymentResultPage />} />
            <Route path="/notifications" element={<NotificationsPage />} />
          </Route>

          {/* Fallback to Home */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
};

export default App;
