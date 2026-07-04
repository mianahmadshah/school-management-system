import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';

const TeacherList = () => {
  const [teachers, setTeachers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchTeachers();
  }, []);

  const fetchTeachers = async () => {
    try {
      const response = await axios.get('/api/v1/teachers/', {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`
        }
      });
      setTeachers(response.data.results || response.data);
    } catch (error) {
      console.error('Error fetching teachers', error);
    } finally {
      setLoading(false);
    }
  };

  const deleteTeacher = async (id) => {
    if (window.confirm('Are you sure you want to delete this teacher?')) {
      try {
        await axios.delete(`/api/v1/teachers/${id}/`, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        });
        fetchTeachers();
      } catch (error) {
        console.error('Error deleting teacher', error);
      }
    }
  };

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Teachers</h1>
        <Link to="/admin/teachers/add" className="bg-blue-600 text-white px-4 py-2 rounded">
          Add Teacher
        </Link>
      </div>

      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50 border-b">
            <tr>
              <th className="p-4 text-left">Name</th>
              <th className="p-4 text-left">Employee ID</th>
              <th className="p-4 text-left">Department</th>
              <th className="p-4 text-left">Actions</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan="4" className="p-4 text-center">Loading...</td>
              </tr>
            ) : teachers.length === 0 ? (
              <tr>
                <td colSpan="4" className="p-4 text-center">No teachers found.</td>
              </tr>
            ) : (
              teachers.map(teacher => (
                <tr key={teacher.id} className="border-b">
                  <td className="p-4">{teacher.user?.first_name} {teacher.user?.last_name}</td>
                  <td className="p-4">{teacher.employee_id}</td>
                  <td className="p-4">{teacher.department}</td>
                  <td className="p-4">
                    <Link to={`/admin/teachers/edit/${teacher.id}`} className="text-blue-600 mr-4">Edit</Link>
                    <button onClick={() => deleteTeacher(teacher.id)} className="text-red-600">Delete</button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default TeacherList;
