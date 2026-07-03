import React from 'react';

const TeacherDashboardCards = () => (
  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
    <div className="bg-blue-500 text-white rounded-lg p-6 shadow">
      <h2 className="text-lg font-semibold">Assigned Classes</h2>
      <p className="text-3xl font-bold mt-2">5</p>
    </div>
    <div className="bg-green-500 text-white rounded-lg p-6 shadow">
      <h2 className="text-lg font-semibold">Assignments</h2>
      <p className="text-3xl font-bold mt-2">12</p>
    </div>
    <div className="bg-yellow-400 text-white rounded-lg p-6 shadow">
      <h2 className="text-lg font-semibold">Attendance Today</h2>
      <p className="text-3xl font-bold mt-2">98%</p>
    </div>
  </div>
);

export default TeacherDashboardCards;