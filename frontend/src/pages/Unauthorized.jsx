import React from 'react';
import { Link } from 'react-router-dom';
import { MdLock } from 'react-icons/md';

const Unauthorized = () => (
  <div className="min-h-screen flex flex-col items-center justify-center bg-slate-50 text-center p-6">
    <MdLock className="text-8xl text-slate-300 mb-4" />
    <h1 className="text-6xl font-bold text-slate-800 mb-2">403</h1>
    <p className="text-slate-500 text-lg mb-6">You do not have permission to access this page.</p>
    <Link to="/" className="btn-primary">Go to Home</Link>
  </div>
);

export default Unauthorized;
