import React from 'react';
import TeacherDashboardCards from '../../components/dashboard/TeacherDashboardCards';
import DashboardTable from '../../components/dashboard/DashboardTable';
import DashboardChart from '../../components/dashboard/DashboardChart';

const tableColumns = ['Student', 'Assignment', 'Status'];
const tableData = [
  { Student: 'Ali', Assignment: 'Math HW', Status: 'Submitted' },
  { Student: 'Sara', Assignment: 'Science Project', Status: 'Pending' },
];

const TeacherDashboard = () => (
  <div className="p-6">
    <TeacherDashboardCards />
    <DashboardTable title="Assignments" columns={tableColumns} data={tableData} />
    <DashboardChart title="Class Performance" />
  </div>
);

export default TeacherDashboard;