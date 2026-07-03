import React from 'react';
import StudentDashboardCards from '../../components/dashboard/StudentDashboardCards';
import DashboardTable from '../../components/dashboard/DashboardTable';
import DashboardChart from '../../components/dashboard/DashboardChart';

const tableColumns = ['Subject', 'Marks', 'Grade'];
const tableData = [
  { Subject: 'Math', Marks: 95, Grade: 'A+' },
  { Subject: 'Science', Marks: 88, Grade: 'A' },
];

const StudentDashboard = () => (
  <div className="p-6">
    <StudentDashboardCards />
    <DashboardTable title="Recent Results" columns={tableColumns} data={tableData} />
    <DashboardChart title="Attendance Trend" />
  </div>
);

export default StudentDashboard;