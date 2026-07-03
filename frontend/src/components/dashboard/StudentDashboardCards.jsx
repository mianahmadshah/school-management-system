import React from 'react';

const StudentDashboardCards = () => (
  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
    <div className="bg-blue-400 text-white rounded-lg p-6 shadow">
      <h2 className="text-lg font-semibold">Attendance</h2>
      <p className="text-3xl font-bold mt-2">95%</p>
    </div>
    <div className="bg-green-400 text-white rounded-lg p-6 shadow">
      <h2 className="text-lg font-semibold">Assignments</h2>
      <p className="text-3xl font-bold mt-2">8</p>
    </div>
    <div className="bg-yellow-300 text-white rounded-lg p-6 shadow">
      <h2 className="text-lg font-semibold">Results</h2>
      <p className="text-3xl font-bold mt-2">A+</p>
    </div>
  </div>
);

export default StudentDashboardCards;