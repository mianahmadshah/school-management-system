import React, { useState, useEffect } from 'react';
import apiClient from '../api/client';

export default function Classes() {
  const [classes, setClasses] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchClasses();
  }, []);

  const fetchClasses = async () => {
    try {
      const res = await apiClient.get('/classes/');
      setClasses(res.data.results || res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">Classes & Sections</h1>
          <p className="text-slate-500">Manage school grades and their respective sections.</p>
        </div>
      </div>

      <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6">
        {loading ? (
          <p className="text-slate-500">Loading...</p>
        ) : classes.length === 0 ? (
          <p className="text-slate-500">No classes found.</p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {classes.map(cls => (
              <div key={cls.id} className="border border-slate-200 p-4 rounded-xl hover:shadow-md transition">
                <h3 className="font-bold text-lg text-slate-800">Grade {cls.grade}</h3>
                <p className="text-slate-500 text-sm">Capacity: {cls.capacity}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
