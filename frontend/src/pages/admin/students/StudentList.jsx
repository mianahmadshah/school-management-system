import React, { useEffect, useState } from 'react';
import studentService from '../../../services/studentService';
import DashboardTable from '../../../components/dashboard/DashboardTable';
import { Link } from 'react-router-dom';

const tableColumns = ['ID', 'Name', 'Email', 'Class', 'Section', 'Actions'];

const StudentList = () => {
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    studentService.getStudents().then(data => {
      setStudents(data);
      setLoading(false);
    });
  }, []);

  const handleDelete = async (id) => {
    await studentService.deleteStudent(id);
    setStudents(students.filter(s => s.id !== id));
  };

  const tableData = students.map(student => ({
    ID: student.id,
    Name: student.name,
    Email: student.email,
    Class: student.class_name,
    Section: student.section_name,
    Actions: (
      <div className="flex gap-2">
        <Link to={`/admin/students/edit/${student.id}`} className="text-blue-600 hover:underline">Edit</Link>
        <button className="text-red-600 hover:underline" onClick={() => handleDelete(student.id)}>Delete</button>
      </div>
    )
  }));

  if (loading) return <div>Loading...</div>;

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-2xl font-bold">Students</h2>
        <Link to="/admin/students/add" className="bg-blue-600 text-white px-4 py-2 rounded">Add Student</Link>
      </div>
      <DashboardTable title="Student List" columns={tableColumns} data={tableData} />
    </div>
  );
};

export default StudentList;