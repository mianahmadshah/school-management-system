import useAuthStore from '../store/authStore';
import { Users, GraduationCap, DollarSign, Activity } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

export default function Dashboard() {
  const user = useAuthStore(state => state.user);
  const { logout } = useAuth();

  const stats = [
    { title: 'Total Students', value: '1,248', icon: Users, color: 'bg-blue-500' },
    { title: 'Total Teachers', value: '84', icon: GraduationCap, color: 'bg-purple-500' },
    { title: 'Fee Collection', value: '$45,200', icon: DollarSign, color: 'bg-emerald-500' },
    { title: 'System Health', value: '98%', icon: Activity, color: 'bg-orange-500' },
  ];

  return (
    <div className="space-y-6">
      <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">
            Welcome back, {user?.first_name || 'Admin'}! 👋
          </h1>
          <p className="text-slate-500 mt-1">Here is what is happening in your school today.</p>
        </div>
        <div className="text-right hidden sm:block">
          <p className="text-sm font-medium text-slate-500">Current Date</p>
          <p className="text-lg font-semibold text-slate-800">
            {new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })}
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, index) => {
          const Icon = stat.icon;
          return (
            <div key={index} className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 hover:shadow-md transition-shadow">
              <div className="flex items-center gap-4">
                <div className={`w-12 h-12 rounded-xl flex items-center justify-center text-white shadow-lg ${stat.color} shadow-${stat.color.replace('bg-', '')}/30`}>
                  <Icon size={24} />
                </div>
                <div>
                  <p className="text-sm font-medium text-slate-500">{stat.title}</p>
                  <p className="text-2xl font-bold text-slate-800">{stat.value}</p>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-white p-6 rounded-2xl shadow-sm border border-slate-100 min-h-[400px]">
          <h3 className="text-lg font-bold text-slate-800 mb-4">Recent Activity</h3>
          {/* We will implement ActivityLog feed here later */}
          <div className="flex items-center justify-center h-64 text-slate-400 border-2 border-dashed border-slate-100 rounded-xl">
            Activity Feed Component (Module 9 Integration coming soon)
          </div>
        </div>
        <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 min-h-[400px]">
          <h3 className="text-lg font-bold text-slate-800 mb-4">Upcoming Classes</h3>
          {/* We will implement Timetable feed here later */}
          <div className="flex items-center justify-center h-64 text-slate-400 border-2 border-dashed border-slate-100 rounded-xl">
            Timetable Component (Module 8 Integration coming soon)
          </div>
        </div>
      </div>

      <div className="flex items-center justify-end">
        <button onClick={logout}>Logout</button>
      </div>
    </div>
  );
}
