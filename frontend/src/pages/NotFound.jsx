import React from 'react';
import { Link } from 'react-router-dom';
import { MdErrorOutline } from 'react-icons/md';

const NotFound = () => (
  <div className="min-h-screen flex flex-col items-center justify-center bg-slate-50 text-center p-6">
    <MdErrorOutline className="text-8xl text-slate-300 mb-4" />
    <h1 className="text-6xl font-bold text-slate-800 mb-2">404</h1>
    <p className="text-slate-500 text-lg mb-6">Oops! The page you are looking for does not exist.</p>
    <Link to="/" className="btn-primary">Go to Home</Link>
  </div>
);

export default NotFound;
