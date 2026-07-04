/**
 * main.jsx
 * Location: frontend/src/main.jsx
 *
 * App entry point. Wraps the app with:
 * - BrowserRouter (for useNavigate in AuthContext)
 * - AuthProvider (global auth state)
 */
import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import App from './App.jsx';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <App />
      </AuthProvider>
    </BrowserRouter>
  </React.StrictMode>
);
