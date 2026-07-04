/**
 * Navbar.jsx
 * Location: frontend/src/components/layout/Navbar.jsx
 *
 * Top navigation bar with:
 * - Dynamic page title (based on current route)
 * - Notification bell
 * - User avatar dropdown with profile/logout
 */
import React, { useState, useRef, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { MdNotifications, MdPerson, MdLogout, MdSettings } from 'react-icons/md';
import { useAuth } from '../../contexts/AuthContext';

// Map route prefixes to readable titles
const PAGE_TITLES = {
  '/admin/students':      'Student Management',
  '/admin/teachers':      'Teacher Management',
  '/admin/classes':       'Class Management',
  '/admin/sections':      'Section Management',
  '/admin/subjects':      'Subject Management',
  '/admin/attendance':    'Attendance',
  '/admin/examinations':  'Examinations',
  '/admin/results':       'Results',
  '/admin/timetable':     'Timetable',
  '/admin/fees':          'Fees & Payments',
  '/admin/announcements': 'Announcements',
  '/admin/users':         'User Management',
  '/admin/activity-logs': 'Activity Logs',
  '/admin/reports':       'Reports',
  '/admin':               'Admin Dashboard',
  '/teacher/attendance':  'Take Attendance',
  '/teacher/assignments': 'Assignments',
  '/teacher/marks':       'Enter Marks',
  '/teacher/students':    'My Students',
  '/teacher/timetable':   'Timetable',
  '/teacher/profile':     'My Profile',
  '/teacher':             'Teacher Dashboard',
  '/student/attendance':  'My Attendance',
  '/student/timetable':   'Timetable',
  '/student/results':     'My Results',
  '/student/assignments': 'Assignments',
  '/student/announcements':'Notices',
  '/student/profile':     'My Profile',
  '/student':             'Student Dashboard',
};

const getPageTitle = (pathname) => {
  // Match the most specific (longest) path first
  const match = Object.keys(PAGE_TITLES)
    .sort((a, b) => b.length - a.length)
    .find((key) => pathname.startsWith(key));
  return PAGE_TITLES[match] || 'Dashboard';
};

const Navbar = () => {
  const { user, logout } = useAuth();
  const location = useLocation();
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const dropdownRef = useRef(null);

  // Close dropdown on outside click
  useEffect(() => {
    const handler = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setDropdownOpen(false);
      }
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  const title = getPageTitle(location.pathname);
  const profilePath = `/${user?.role}/profile`;

  return (
    <header className="h-16 bg-white border-b border-slate-200 flex items-center justify-between px-6 sticky top-0 z-30 shadow-sm">
      
      {/* Page Title */}
      <h1 className="text-lg font-semibold text-slate-800">{title}</h1>

      {/* Right section */}
      <div className="flex items-center gap-3">
        
        {/* Notification bell */}
        <button className="relative p-2 text-slate-500 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors">
          <MdNotifications className="text-xl" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full" />
        </button>

        {/* User avatar + dropdown */}
        <div className="relative" ref={dropdownRef}>
          <button
            onClick={() => setDropdownOpen((v) => !v)}
            className="flex items-center gap-2 p-1.5 rounded-lg hover:bg-slate-100 transition-colors"
          >
            <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center text-white font-bold text-sm">
              {user?.first_name?.charAt(0)?.toUpperCase() || 'U'}
            </div>
            <div className="hidden sm:block text-left">
              <p className="text-sm font-semibold text-slate-700 leading-tight">
                {user?.first_name} {user?.last_name}
              </p>
              <p className="text-xs text-slate-400 capitalize">{user?.role}</p>
            </div>
          </button>

          {/* Dropdown */}
          {dropdownOpen && (
            <div className="absolute right-0 top-full mt-2 w-48 bg-white border border-slate-200 rounded-xl shadow-lg overflow-hidden z-50">
              <Link
                to={profilePath}
                onClick={() => setDropdownOpen(false)}
                className="flex items-center gap-3 px-4 py-3 text-sm text-slate-700 hover:bg-slate-50 transition-colors"
              >
                <MdPerson className="text-slate-400" />
                My Profile
              </Link>
              <button
                onClick={() => { setDropdownOpen(false); logout(); }}
                className="flex items-center gap-3 px-4 py-3 text-sm text-red-500 hover:bg-red-50 transition-colors w-full text-left border-t border-slate-100"
              >
                <MdLogout className="text-red-400" />
                Logout
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};

export default Navbar;
