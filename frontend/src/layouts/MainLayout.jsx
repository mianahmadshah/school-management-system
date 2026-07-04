/**
 * MainLayout.jsx
 * Location: frontend/src/layouts/MainLayout.jsx
 *
 * Shell that wraps all protected dashboard pages.
 * Structure:
 *   ┌────────────┬────────────────────────────────┐
 *   │  Sidebar   │  Navbar                        │
 *   │  (fixed)   ├────────────────────────────────┤
 *   │            │  <Outlet /> (page content)     │
 *   └────────────┴────────────────────────────────┘
 */
import React from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from '../components/layout/Sidebar';
import Navbar from '../components/layout/Navbar';
import { Toaster } from 'react-hot-toast';

const MainLayout = () => {
  return (
    <div className="flex h-screen bg-slate-50 overflow-hidden">
      {/* Fixed Left Sidebar — 256px wide */}
      <Sidebar />

      {/* Right side: Navbar + scrollable page content */}
      <div className="flex flex-col flex-1 ml-64 min-w-0 h-screen overflow-hidden">
        {/* Sticky top navbar */}
        <Navbar />

        {/* Scrollable content area */}
        <main className="flex-1 overflow-y-auto p-6 scrollbar-thin">
          <Outlet />
        </main>
      </div>

      {/* Global toast notifications */}
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 3500,
          style: {
            borderRadius: '10px',
            fontSize: '14px',
            fontFamily: 'Inter, sans-serif',
          },
          success: {
            style: { background: '#f0fdf4', color: '#166534', border: '1px solid #bbf7d0' },
            iconTheme: { primary: '#16a34a', secondary: '#fff' },
          },
          error: {
            style: { background: '#fef2f2', color: '#991b1b', border: '1px solid #fecaca' },
            iconTheme: { primary: '#dc2626', secondary: '#fff' },
          },
        }}
      />
    </div>
  );
};

export default MainLayout;
