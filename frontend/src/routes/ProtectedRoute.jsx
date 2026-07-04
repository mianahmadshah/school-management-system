/**
 * ProtectedRoute.jsx
 * Location: frontend/src/routes/ProtectedRoute.jsx
 *
 * Guards routes based on:
 * 1. Authentication — if not logged in → redirect to /login
 * 2. Role — if wrong role → redirect to /unauthorized
 *
 * Usage:
 *   <ProtectedRoute allowedRoles={['admin']}>
 *     <AdminDashboard />
 *   </ProtectedRoute>
 */
import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const ProtectedRoute = ({ allowedRoles, children }) => {
  const { user, loading } = useAuth();

  // Show nothing while checking localStorage session
  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-slate-50">
        <div className="flex flex-col items-center gap-3">
          <div className="w-10 h-10 border-4 border-blue-600 border-t-transparent rounded-full animate-spin" />
          <p className="text-slate-500 text-sm font-medium">Loading...</p>
        </div>
      </div>
    );
  }

  // Not logged in
  if (!user) return <Navigate to="/login" replace />;

  // Wrong role
  if (allowedRoles && !allowedRoles.includes(user.role)) {
    return <Navigate to="/unauthorized" replace />;
  }

  // Render children or nested routes via Outlet
  return children ? children : <Outlet />;
};

export default ProtectedRoute;
