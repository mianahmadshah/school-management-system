import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import apiClient from '../api/client';
import useAuthStore from '../store/authStore';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  
  const navigate = useNavigate();
  const login = useAuthStore((state) => state.login);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      // 1. Get tokens
      const tokenRes = await apiClient.post('/auth/login/', { email, password });
      const { access, refresh } = tokenRes.data;

      // 2. We could decode the JWT here, or call a /profile endpoint to get user details
      // Since our API currently requires the token, we set it in state first (hacky, but works)
      // Or we can just set it and redirect, letting Dashboard fetch profile. 
      // But let's temporarily set it in zustand so the apiClient interceptor uses it:
      useAuthStore.getState().setAccessToken(access);
      
      const profileRes = await apiClient.get('/auth/profile/');
      
      // 3. Save to global state
      login(profileRes.data, access, refresh);
      
      // 4. Redirect
      navigate('/dashboard', { replace: true });
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || 'Failed to login. Please check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="glass p-8 rounded-2xl w-full">
      <div className="text-center mb-8">
        <div className="w-16 h-16 bg-primary-500 rounded-2xl shadow-lg shadow-primary-500/30 mx-auto mb-4 flex items-center justify-center">
          <span className="text-2xl text-white font-bold tracking-tighter">EC</span>
        </div>
        <h1 className="text-2xl font-bold text-slate-800">Welcome Back</h1>
        <p className="text-slate-500 mt-2">Sign in to your EduCore account</p>
      </div>

      {error && (
        <div className="bg-red-50 text-red-600 p-3 rounded-lg text-sm mb-6 border border-red-100">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-5">
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Email Address</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 transition-all bg-white/50"
            placeholder="admin@school.com"
            required
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Password</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 transition-all bg-white/50"
            placeholder="••••••••"
            required
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full py-3 px-4 bg-primary-600 hover:bg-primary-700 text-white font-medium rounded-xl shadow-lg shadow-primary-500/20 transition-all active:scale-[0.98] disabled:opacity-70 disabled:pointer-events-none mt-2"
        >
          {loading ? 'Signing in...' : 'Sign In'}
        </button>
      </form>
    </div>
  );
}
