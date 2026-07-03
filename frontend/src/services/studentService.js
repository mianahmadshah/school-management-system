import axios from 'axios';

const API_URL = '/api/v1/students/';

const getStudents = async () => {
  const res = await axios.get(API_URL);
  return res.data;
};

const getStudent = async (id) => {
  const res = await axios.get(`${API_URL}${id}/`);
  return res.data;
};

const addStudent = async (student) => {
  const res = await axios.post(API_URL, student);
  return res.data;
};

const updateStudent = async (id, student) => {
  const res = await axios.put(`${API_URL}${id}/`, student);
  return res.data;
};

const deleteStudent = async (id) => {
  await axios.delete(`${API_URL}${id}/`);
};

const studentService = {
  getStudents,
  getStudent,
  addStudent,
  updateStudent,
  deleteStudent,
};

export default studentService;