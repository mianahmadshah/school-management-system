/**
 * Admin Dashboard
 * Location: frontend/src/pages/admin/Dashboard.jsx
 *
 * Shows live statistics fetched from the backend API.
 * Stats: Total Students, Teachers, Classes, Sections, Fees collected, etc.
 */
import React, { useEffect, useState } from 'react';
import { MdPeople, MdSchool, MdClass, MdAttachMoney, MdEventNote, MdCampaign } from 'react-icons/md';
import { studentService, teacherService, classService, feeService } from '../../api/services';
import { useAuth } from '../../contexts/AuthContext';

const StatCard = ({ icon: Icon, label, value, color, bgColor }) => (
  <div className="card p-5 flex items-center gap-4">
    <div className={`stat-icon ${bgColor}`}>
      <Icon className={`text-2xl ${color}`} />
    </div>
    <div>
      <p className="text-sm text-slate-500 font-medium">{label}</p>
      <p className="text-2xl font-bold text-slate-800 mt-0.5">
        {value !== null ? value : <span className="w-12 h-6 bg-slate-200 animate-pulse rounded inline-block" />}
      </p>
    </div>
  </div>
);

const AdminDashboard = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState({ students: null, teachers: null, classes: null });

  useEffect(() => {
    // Fetch counts from API
    const fetchStats = async () => {
      try {
        const [stuRes, teaRes, clsRes] = await Promise.allSettled([
          studentService.list({ page_size: 1 }),
          teacherService.list({ page_size: 1 }),
          classService.list({ page_size: 1 }),
        ]);
        setStats({
          students: stuRes.status === 'fulfilled' ? (stuRes.value.data.count ?? stuRes.value.data.length) : 'N/A',
          teachers: teaRes.status === 'fulfilled' ? (teaRes.value.data.count ?? teaRes.value.data.length) : 'N/A',
          classes:  clsRes.status === 'fulfilled' ? (clsRes.value.data.count ?? clsRes.value.data.length) : 'N/A',
        });
      } catch (e) {
        console.error(e);
      }
    };
    fetchStats();
  }, []);

  const statCards = [
    { icon: MdPeople,     label: 'Total Students', value: stats.students, color: 'text-blue-600',   bgColor: 'bg-blue-50' },
    { icon: MdSchool,     label: 'Total Teachers', value: stats.teachers, color: 'text-green-600',  bgColor: 'bg-green-50' },
    { icon: MdClass,      label: 'Total Classes',  value: stats.classes,  color: 'text-purple-600', bgColor: 'bg-purple-50' },
    { icon: MdAttachMoney,label: 'Fee Collected',  value: 'PKR 0',        color: 'text-yellow-600', bgColor: 'bg-yellow-50' },
    { icon: MdEventNote,  label: 'Attendance Today',value: '—',           color: 'text-pink-600',   bgColor: 'bg-pink-50' },
    { icon: MdCampaign,   label: 'Announcements',  value: '—',            color: 'text-indigo-600', bgColor: 'bg-indigo-50' },
  ];

  return (
    <div className="space-y-6">
      {/* Welcome */}
      <div>
        <h2 className="text-2xl font-bold text-slate-800">
          Welcome back, {user?.first_name}! 👋
        </h2>
        <p className="text-slate-500 text-sm mt-1">
          Here is what is happening in your school today.
        </p>
      </div>

      {/* Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
        {statCards.map((card) => (
          <StatCard key={card.label} {...card} />
        ))}
      </div>

      {/* Quick Links */}
      <div className="card">
        <div className="card-header">
          <h3 className="font-semibold text-slate-800">Quick Actions</h3>
        </div>
        <div className="card-body grid grid-cols-2 md:grid-cols-4 gap-3">
          {[
            { label: 'Add Student',   href: '/admin/students/new',     emoji: '🎓' },
            { label: 'Add Teacher',   href: '/admin/teachers/new',     emoji: '👨‍🏫' },
            { label: 'Mark Attendance',href: '/admin/attendance',      emoji: '📋' },
            { label: 'Post Announcement',href: '/admin/announcements', emoji: '📢' },
          ].map(({ label, href, emoji }) => (
            <a
              key={label}
              href={href}
              className="flex flex-col items-center justify-center gap-2 p-4 rounded-xl border border-slate-200 hover:border-blue-300 hover:bg-blue-50 transition-all text-center group"
            >
              <span className="text-2xl">{emoji}</span>
              <span className="text-xs font-medium text-slate-600 group-hover:text-blue-700">{label}</span>
            </a>
          ))}
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;