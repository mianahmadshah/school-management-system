import React from 'react';
import AdminDashboardCards from '../../components/dashboard/AdminDashboardCards';
import DashboardTable from '../../components/dashboard/DashboardTable';
import DashboardChart from '../../components/dashboard/DashboardChart';

const tableColumns = ['Name', 'Role', 'Status'];
const tableData = [
  { Name: 'John Doe', Role: 'Student', Status: 'Active' },
  { Name: 'Jane Smith', Role: 'Teacher', Status: 'Active' },
];

const AdminDashboard = () => (
  <div className="p-6">
    <AdminDashboardCards />
    <DashboardTable title="Recent Users" columns={tableColumns} data={tableData} />
    <DashboardChart title="Attendance Overview" />
  </div>
);

export default AdminDashboard;