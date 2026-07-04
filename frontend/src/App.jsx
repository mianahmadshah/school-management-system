/**
 * App.jsx
 * Location: frontend/src/App.jsx
 *
 * Root router. All routes are defined here.
 * Clean separation: public routes vs protected role-based routes.
 *
 * Route Structure:
 *   /login               → Login page (public)
 *   /forgot-password     → ForgotPassword (public)
 *   /unauthorized        → Unauthorized page (public)
 *
 *   /admin/*             → MainLayout + Admin pages (role: admin)
 *   /teacher/*           → MainLayout + Teacher pages (role: teacher)
 *   /student/*           → MainLayout + Student pages (role: student)
 */
import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './contexts/AuthContext';
import ProtectedRoute from './routes/ProtectedRoute';
import MainLayout from './layouts/MainLayout';

// ── Auth Pages ────────────────────────────────────────────────
import Login from './pages/auth/Login';

// ── Admin Pages ───────────────────────────────────────────────
import AdminDashboard from './pages/admin/Dashboard';

// ── Teacher Pages ─────────────────────────────────────────────
import TeacherDashboard from './pages/teacher/Dashboard';

// ── Student Pages ─────────────────────────────────────────────
import StudentDashboard from './pages/student/Dashboard';

// ── Shared ────────────────────────────────────────────────────
import NotFound from './pages/NotFound';
import Unauthorized from './pages/Unauthorized';

const App = () => {
  return (
    <Routes>
      {/* ── Public Routes ──────────────────────────────── */}
      <Route path="/login" element={<Login />} />
      <Route path="/unauthorized" element={<Unauthorized />} />

      {/* ── Admin Routes ───────────────────────────────── */}
      <Route
        element={
          <ProtectedRoute allowedRoles={['admin']}>
            <MainLayout />
          </ProtectedRoute>
        }
      >
        <Route path="/admin" element={<AdminDashboard />} />
        {/* All other admin pages added here as we build them */}
      </Route>

      {/* ── Teacher Routes ─────────────────────────────── */}
      <Route
        element={
          <ProtectedRoute allowedRoles={['teacher']}>
            <MainLayout />
          </ProtectedRoute>
        }
      >
        <Route path="/teacher" element={<TeacherDashboard />} />
      </Route>

      {/* ── Student Routes ─────────────────────────────── */}
      <Route
        element={
          <ProtectedRoute allowedRoles={['student']}>
            <MainLayout />
          </ProtectedRoute>
        }
      >
        <Route path="/student" element={<StudentDashboard />} />
      </Route>

      {/* ── Default Redirect ────────────────────────────── */}
      <Route path="/" element={<Navigate to="/login" replace />} />

      {/* ── 404 ─────────────────────────────────────────── */}
      <Route path="*" element={<NotFound />} />
    </Routes>
  );
};

export default App;
