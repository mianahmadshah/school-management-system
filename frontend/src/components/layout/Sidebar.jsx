import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

const navLinks = {
  admin: [
    { to: '/admin', label: 'Dashboard' },
    { to: '/profile', label: 'Profile' },
    // Add more admin links here
  ],
  teacher: [
    { to: '/teacher', label: 'Dashboard' },
    { to: '/profile', label: 'Profile' },
    // Add more teacher links here
  ],
  student: [
    { to: '/student', label: 'Dashboard' },
    { to: '/profile', label: 'Profile' },
    // Add more student links here
  ],
};

const Sidebar = () => {
  const { user, logout } = useAuth();
  const location = useLocation();
  const role = user?.role;
  const links = navLinks[role] || [];

  return (
    <aside className="w-64 h-screen bg-white shadow-md p-4">
      <nav>
        <ul>
          {links.map(link => (
            <li key={link.to} className={location.pathname === link.to ? 'font-bold text-blue-600 mb-4' : 'mb-4'}>
              <Link to={link.to}>{link.label}</Link>
            </li>
          ))}
          <li>
            <button onClick={logout} className="text-red-500 hover:underline">Logout</button>
          </li>
        </ul>
      </nav>
    </aside>
  );
};

export default Sidebar;
