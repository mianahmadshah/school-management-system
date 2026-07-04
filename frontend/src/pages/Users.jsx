import { useState, useEffect } from 'react';
import apiClient from '../api/client';
import { UserPlus, Search, Edit2, Trash2 } from 'lucide-react';

export default function Users() {
  const [activeTab, setActiveTab] = useState('students');
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, [activeTab]);

  const fetchData = async () => {
    setLoading(true);
    try {
      const endpoint = activeTab === 'students' ? '/students/' : '/teachers/';
      const response = await apiClient.get(endpoint);
      setData(response.data.results || response.data);
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">User Management</h1>
          <p className="text-slate-500">Manage students and teachers across the system.</p>
        </div>
        <button className="flex items-center gap-2 bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-lg font-medium transition-colors shadow-sm">
          <UserPlus size={18} />
          Add New {activeTab === 'students' ? 'Student' : 'Teacher'}
        </button>
      </div>

      <div className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
        {/* Tabs & Search */}
        <div className="border-b border-slate-200 p-4 flex flex-col sm:flex-row justify-between gap-4">
          <div className="flex space-x-1 bg-slate-100 p-1 rounded-lg self-start">
            <button
              onClick={() => setActiveTab('students')}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                activeTab === 'students' ? 'bg-white text-slate-800 shadow' : 'text-slate-500 hover:text-slate-700'
              }`}
            >
              Students
            </button>
            <button
              onClick={() => setActiveTab('teachers')}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                activeTab === 'teachers' ? 'bg-white text-slate-800 shadow' : 'text-slate-500 hover:text-slate-700'
              }`}
            >
              Teachers
            </button>
          </div>
          
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
            <input 
              type="text" 
              placeholder={`Search ${activeTab}...`} 
              className="pl-10 pr-4 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 w-full sm:w-64"
            />
          </div>
        </div>

        {/* Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-50 text-slate-500 text-sm border-b border-slate-200">
                <th className="py-3 px-6 font-medium">Name</th>
                <th className="py-3 px-6 font-medium">Email / Contact</th>
                {activeTab === 'students' ? (
                  <>
                    <th className="py-3 px-6 font-medium">Enrollment No.</th>
                    <th className="py-3 px-6 font-medium">Class</th>
                  </>
                ) : (
                  <>
                    <th className="py-3 px-6 font-medium">Employee ID</th>
                    <th className="py-3 px-6 font-medium">Department</th>
                  </>
                )}
                <th className="py-3 px-6 font-medium text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan="5" className="py-8 text-center text-slate-400">Loading...</td>
                </tr>
              ) : data.length === 0 ? (
                <tr>
                  <td colSpan="5" className="py-8 text-center text-slate-400">No {activeTab} found.</td>
                </tr>
              ) : (
                data.map((item) => (
                  <tr key={item.id} className="border-b border-slate-100 hover:bg-slate-50/50 transition-colors">
                    <td className="py-3 px-6">
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-full bg-primary-100 text-primary-700 flex items-center justify-center font-bold text-sm">
                          {item.user?.full_name?.charAt(0) || 'U'}
                        </div>
                        <span className="font-medium text-slate-700">{item.user?.full_name}</span>
                      </div>
                    </td>
                    <td className="py-3 px-6 text-sm text-slate-500">
                      <div>{item.user?.email}</div>
                      <div className="text-xs">{item.contact_number || '-'}</div>
                    </td>
                    {activeTab === 'students' ? (
                      <>
                        <td className="py-3 px-6 text-sm font-medium text-slate-600">{item.enrollment_number}</td>
                        <td className="py-3 px-6 text-sm text-slate-600">
                          {item.current_class ? `${item.current_class.grade} - ${item.current_section?.name || ''}` : 'Not Assigned'}
                        </td>
                      </>
                    ) : (
                      <>
                        <td className="py-3 px-6 text-sm font-medium text-slate-600">{item.employee_id}</td>
                        <td className="py-3 px-6 text-sm text-slate-600">{item.department || '-'}</td>
                      </>
                    )}
                    <td className="py-3 px-6 text-right">
                      <div className="flex justify-end gap-2">
                        <button className="p-1.5 text-slate-400 hover:text-blue-600 hover:bg-blue-50 rounded-md transition-colors">
                          <Edit2 size={16} />
                        </button>
                        <button className="p-1.5 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-md transition-colors">
                          <Trash2 size={16} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
