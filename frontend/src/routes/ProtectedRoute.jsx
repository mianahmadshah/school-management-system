import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const ProtectedRoute = ({ children, allowedRoles }) => {
  const { user, loading } = useAuth();

  if (loading) return <div>Loading...</div>;
  if (!user) return <Navigate to="/login" />;
  if (allowedRoles && !allowedRoles.includes(user.role)) return <Navigate to="/unauthorized" />;
  return children;
};

export default ProtectedRoute;

// Usage example in App.jsx
// <Route
//   path="/admin"
//   element={
//     <ProtectedRoute allowedRoles={['admin']}>
//       <AdminDashboard />
//     </ProtectedRoute>
//   }
// />
