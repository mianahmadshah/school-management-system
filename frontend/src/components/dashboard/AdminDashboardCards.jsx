import React from 'react';

const AdminDashboardCards = () => (
  <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
    <div className="bg-blue-600 text-white rounded-lg p-6 shadow">
      <h2 className="text-lg font-semibold">Total Students</h2>
      <p className="text-3xl font-bold mt-2">1,200</p>
    </div>
    <div className="bg-green-600 text-white rounded-lg p-6 shadow">
      <h2 className="text-lg font-semibold">Total Teachers</h2>
      <p className="text-3xl font-bold mt-2">75</p>
    </div>
    <div className="bg-yellow-500 text-white rounded-lg p-6 shadow">
      <h2 className="text-lg font-semibold">Classes</h2>
      <p className="text-3xl font-bold mt-2">30</p>
    </div>
    <div className="bg-purple-600 text-white rounded-lg p-6 shadow">
      <h2 className="text-lg font-semibold">Sections</h2>
      <p className="text-3xl font-bold mt-2">90</p>
    </div>
  </div>
);

export default AdminDashboardCards;