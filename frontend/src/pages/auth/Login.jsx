/**
 * Login.jsx
 * Location: frontend/src/pages/auth/Login.jsx
 *
 * Production-quality login page:
 * - Blue gradient background with geometric pattern
 * - Glass card form
 * - React Hook Form validation
 * - Toast notifications for success/error
 * - Loading spinner on submit
 */
import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { MdSchool, MdEmail, MdLock, MdVisibility, MdVisibilityOff } from 'react-icons/md';
import { Link } from 'react-router-dom';
import toast from 'react-hot-toast';
import { Toaster } from 'react-hot-toast';
import { useAuth } from '../../contexts/AuthContext';

const Login = () => {
  const { login } = useAuth();
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm();

  const onSubmit = async ({ email, password }) => {
    setIsLoading(true);
    try {
      await login(email, password);
      toast.success('Welcome back! Redirecting...');
    } catch (err) {
      const message =
        err?.response?.data?.detail ||
        err?.response?.data?.non_field_errors?.[0] ||
        'Invalid email or password.';
      toast.error(message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      <Toaster position="top-right" />

      {/* Full page layout */}
      <div className="min-h-screen flex">

        {/* ─── Left Panel: Brand ──────────────────────────────── */}
        <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-blue-900 via-blue-800 to-blue-700 flex-col items-center justify-center p-12 relative overflow-hidden">
          {/* Decorative circles */}
          <div className="absolute top-[-80px] left-[-80px] w-80 h-80 bg-white/5 rounded-full" />
          <div className="absolute bottom-[-60px] right-[-60px] w-64 h-64 bg-white/5 rounded-full" />
          <div className="absolute top-1/3 right-[-40px] w-48 h-48 bg-blue-500/20 rounded-full" />

          <div className="relative z-10 text-center">
            <div className="w-20 h-20 bg-white rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-xl">
              <MdSchool className="text-blue-700 text-4xl" />
            </div>
            <h1 className="text-4xl font-bold text-white mb-4">EduCore SMS</h1>
            <p className="text-blue-200 text-lg mb-8 max-w-sm">
              A complete School Management System for Admins, Teachers, and Students.
            </p>
            <div className="grid grid-cols-2 gap-4 text-left max-w-xs mx-auto">
              {[
                ['📊', 'Admin Dashboard'],
                ['📋', 'Attendance Tracking'],
                ['🎓', 'Exam & Results'],
                ['💰', 'Fee Management'],
              ].map(([icon, label]) => (
                <div key={label} className="flex items-center gap-2 text-blue-100 text-sm">
                  <span>{icon}</span>
                  <span>{label}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* ─── Right Panel: Login Form ─────────────────────────── */}
        <div className="flex-1 flex items-center justify-center p-6 bg-slate-50">
          <div className="w-full max-w-md">

            {/* Mobile logo */}
            <div className="flex items-center justify-center gap-3 mb-8 lg:hidden">
              <div className="w-10 h-10 bg-blue-700 rounded-xl flex items-center justify-center">
                <MdSchool className="text-white text-2xl" />
              </div>
              <span className="text-2xl font-bold text-slate-800">EduCore SMS</span>
            </div>

            <div className="bg-white rounded-2xl shadow-lg border border-slate-200 p-8">
              <div className="mb-7">
                <h2 className="text-2xl font-bold text-slate-800">Sign in</h2>
                <p className="text-slate-500 text-sm mt-1">
                  Enter your credentials to access your dashboard.
                </p>
              </div>

              <form onSubmit={handleSubmit(onSubmit)} className="space-y-5" noValidate>

                {/* Email */}
                <div>
                  <label className="form-label">Email Address</label>
                  <div className="relative">
                    <MdEmail className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 text-lg" />
                    <input
                      {...register('email', {
                        required: 'Email is required',
                        pattern: {
                          value: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
                          message: 'Enter a valid email address',
                        },
                      })}
                      type="email"
                      placeholder="admin@school.com"
                      className="form-input pl-10"
                      autoComplete="email"
                    />
                  </div>
                  {errors.email && (
                    <p className="form-error">{errors.email.message}</p>
                  )}
                </div>

                {/* Password */}
                <div>
                  <div className="flex items-center justify-between mb-1.5">
                    <label className="form-label mb-0">Password</label>
                    <Link
                      to="/forgot-password"
                      className="text-xs text-blue-600 hover:text-blue-700 font-medium"
                    >
                      Forgot password?
                    </Link>
                  </div>
                  <div className="relative">
                    <MdLock className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 text-lg" />
                    <input
                      {...register('password', {
                        required: 'Password is required',
                        minLength: { value: 6, message: 'Minimum 6 characters' },
                      })}
                      type={showPassword ? 'text' : 'password'}
                      placeholder="••••••••"
                      className="form-input pl-10 pr-10"
                      autoComplete="current-password"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword((v) => !v)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
                      tabIndex={-1}
                    >
                      {showPassword ? <MdVisibilityOff /> : <MdVisibility />}
                    </button>
                  </div>
                  {errors.password && (
                    <p className="form-error">{errors.password.message}</p>
                  )}
                </div>

                {/* Submit */}
                <button
                  type="submit"
                  disabled={isLoading}
                  className="btn-primary w-full py-3 text-base mt-2"
                >
                  {isLoading ? (
                    <>
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                      Signing in...
                    </>
                  ) : (
                    'Sign In'
                  )}
                </button>
              </form>

              {/* Footer info */}
              <p className="text-center text-xs text-slate-400 mt-6">
                EduCore School Management System &copy; {new Date().getFullYear()}
              </p>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default Login;
