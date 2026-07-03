import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import studentService from '../../../services/studentService';

const StudentForm = () => {
  const [form, setForm] = useState({ name: '', email: '', class_name: '', section_name: '' });
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { id } = useParams();

  useEffect(() => {
    if (id) {
      studentService.getStudent(id).then(data => setForm(data));
    }
  }, [id]);

  const handleChange = e => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async e => {
    e.preventDefault();
    setLoading(true);
    if (id) {
      await studentService.updateStudent(id, form);
    } else {
      await studentService.addStudent(form);
    }
    setLoading(false);
    navigate('/admin/students');
  };

  return (
    <div className="p-6 max-w-lg mx-auto">
      <h2 className="text-2xl font-bold mb-4">{id ? 'Edit Student' : 'Add Student'}</h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        <input name="name" value={form.name} onChange={handleChange} required placeholder="Name" className="w-full border p-2 rounded" />
        <input name="email" value={form.email} onChange={handleChange} required placeholder="Email" className="w-full border p-2 rounded" />
        <input name="class_name" value={form.class_name} onChange={handleChange} required placeholder="Class" className="w-full border p-2 rounded" />
        <input name="section_name" value={form.section_name} onChange={handleChange} required placeholder="Section" className="w-full border p-2 rounded" />
        <button type="submit" className="bg-blue-600 text-white px-4 py-2 rounded" disabled={loading}>
          {loading ? 'Saving...' : id ? 'Update' : 'Add'}
        </button>
      </form>
    </div>
  );
};

export default StudentForm;