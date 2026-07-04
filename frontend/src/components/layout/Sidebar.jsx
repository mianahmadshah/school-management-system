/**
 * Sidebar.jsx
 * Location: frontend/src/components/layout/Sidebar.jsx
 *
 * Role-based sidebar with full navigation for Admin, Teacher, Student.
 * - Shows only the links relevant to the logged-in role
 * - Highlights the active link
 * - Has a collapsible design on mobile
 */
import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  MdDashboard, MdPeople, MdSchool, MdClass, MdViewModule,
  MdMenuBook, MdEventNote, MdAssignment, MdBarChart, MdAttachMoney,
  MdCampaign, MdSchedule, MdHistory, MdPerson, MdLogout,
  MdSupervisorAccount, MdGrade
} from 'react-icons/md';
import { useAuth } from '../../contexts/AuthContext';
import { clsx } from 'clsx';

// ── Navigation definitions per role ──────────────────────────
const NAV = {
  admin: [
    { to: '/admin',              label: 'Dashboard',       icon: MdDashboard },
    { to: '/admin/students',     label: 'Students',        icon: MdPeople },
    { to: '/admin/teachers',     label: 'Teachers',        icon: MdSchool },
    { to: '/admin/classes',      label: 'Classes',         icon: MdClass },
    { to: '/admin/sections',     label: 'Sections',        icon: MdViewModule },
    { to: '/admin/subjects',     label: 'Subjects',        icon: MdMenuBook },
    { to: '/admin/attendance',   label: 'Attendance',      icon: MdEventNote },
    { to: '/admin/examinations', label: 'Examinations',    icon: MdAssignment },
    { to: '/admin/results',      label: 'Results',         icon: MdGrade },
    { to: '/admin/timetable',    label: 'Timetable',       icon: MdSchedule },
    { to: '/admin/fees',         label: 'Fees',            icon: MdAttachMoney },
    { to: '/admin/announcements',label: 'Announcements',   icon: MdCampaign },
    { to: '/admin/users',        label: 'User Management', icon: MdSupervisorAccount },
    { to: '/admin/activity-logs',label: 'Activity Logs',   icon: MdHistory },
    { to: '/admin/reports',      label: 'Reports',         icon: MdBarChart },
  ],
  teacher: [
    { to: '/teacher',              label: 'Dashboard',        icon: MdDashboard },
    { to: '/teacher/attendance',   label: 'Take Attendance',  icon: MdEventNote },
    { to: '/teacher/assignments',  label: 'Assignments',      icon: MdAssignment },
    { to: '/teacher/marks',        label: 'Enter Marks',      icon: MdGrade },
    { to: '/teacher/students',     label: 'My Students',      icon: MdPeople },
    { to: '/teacher/timetable',    label: 'Timetable',        icon: MdSchedule },
    { to: '/teacher/profile',      label: 'Profile',          icon: MdPerson },
  ],
  student: [
    { to: '/student',              label: 'Dashboard',        icon: MdDashboard },
    { to: '/student/attendance',   label: 'My Attendance',    icon: MdEventNote },
    { to: '/student/timetable',    label: 'Timetable',        icon: MdSchedule },
    { to: '/student/results',      label: 'Results',          icon: MdGrade },
    { to: '/student/assignments',  label: 'Assignments',      icon: MdAssignment },
    { to: '/student/announcements',label: 'Notices',          icon: MdCampaign },
    { to: '/student/profile',      label: 'Profile',          icon: MdPerson },
  ],
};

const Sidebar = () => {
  const { user, logout } = useAuth();
  const location = useLocation();
  const links = NAV[user?.role] || [];

  const isActive = (path) =>
    path === `/${user?.role}`
      ? location.pathname === path
      : location.pathname.startsWith(path);

  return (
    <aside className="fixed top-0 left-0 h-screen w-64 bg-gradient-to-b from-blue-900 to-blue-800 flex flex-col z-40 overflow-hidden">
      
      {/* Logo */}
      <div className="flex items-center gap-3 px-5 py-5 border-b border-blue-700/50">
        <div className="w-9 h-9 bg-white rounded-lg flex items-center justify-center flex-shrink-0">
          <MdSchool className="text-blue-700 text-xl" />
        </div>
        <div>
          <p className="text-white font-bold text-base leading-tight">EduCore</p>
          <p className="text-blue-300 text-xs capitalize">{user?.role} Panel</p>
        </div>
      </div>

      {/* Nav Links */}
      <nav className="flex-1 overflow-y-auto scrollbar-thin px-3 py-4 space-y-0.5">
        {links.map(({ to, label, icon: Icon }) => (
          <Link
            key={to}
            to={to}
            className={clsx(
              'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-150',
              isActive(to)
                ? 'bg-white/15 text-white'
                : 'text-blue-200 hover:text-white hover:bg-white/10'
            )}
          >
            <Icon className="text-lg flex-shrink-0" />
            <span>{label}</span>
          </Link>
        ))}
      </nav>

      {/* User + Logout at bottom */}
      <div className="border-t border-blue-700/50 p-4">
        <div className="flex items-center gap-3 mb-3 px-1">
          <div className="w-8 h-8 rounded-full bg-blue-600 border-2 border-blue-400 flex items-center justify-center text-white font-bold text-sm flex-shrink-0">
            {user?.first_name?.charAt(0)?.toUpperCase() || 'U'}
          </div>
          <div className="overflow-hidden">
            <p className="text-white text-sm font-semibold truncate">
              {user?.first_name} {user?.last_name}
            </p>
            <p className="text-blue-300 text-xs truncate">{user?.email}</p>
          </div>
        </div>
        <button
          onClick={logout}
          className="flex items-center gap-2 w-full px-3 py-2 rounded-lg text-sm text-red-300 hover:text-white hover:bg-red-500/20 transition-all duration-150"
        >
          <MdLogout className="text-lg" />
          <span>Logout</span>
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;
