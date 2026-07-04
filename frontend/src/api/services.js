/**
 * services.js
 * Location: frontend/src/api/services.js
 *
 * Centralised API service functions.
 * Every component imports from here — never calls axios directly.
 * This makes it easy to change URLs or add logic in one place.
 */
import axiosInstance from './axiosInstance';

// ─── AUTH ──────────────────────────────────────────────────────
export const authService = {
  login: (data) => axiosInstance.post('/auth/login/', data),
  logout: (refreshToken) => axiosInstance.post('/auth/logout/', { refresh_token: refreshToken }),
  getProfile: () => axiosInstance.get('/auth/profile/'),
  updateProfile: (data) => axiosInstance.patch('/auth/profile/', data),
  changePassword: (data) => axiosInstance.post('/auth/change-password/', data),
  forgotPassword: (data) => axiosInstance.post('/auth/password-reset/', data),
  resetPassword: (data) => axiosInstance.post('/auth/password-reset-confirm/', data),
};

// ─── USERS (Admin) ─────────────────────────────────────────────
export const userService = {
  list: (params) => axiosInstance.get('/auth/users/', { params }),
  get: (id) => axiosInstance.get(`/auth/users/${id}/`),
  create: (data) => axiosInstance.post('/auth/users/', data),
  update: (id, data) => axiosInstance.patch(`/auth/users/${id}/`, data),
  delete: (id) => axiosInstance.delete(`/auth/users/${id}/`),
};

// ─── STUDENTS ──────────────────────────────────────────────────
export const studentService = {
  list: (params) => axiosInstance.get('/students/', { params }),
  get: (id) => axiosInstance.get(`/students/${id}/`),
  create: (data) => axiosInstance.post('/students/', data),
  update: (id, data) => axiosInstance.patch(`/students/${id}/`, data),
  delete: (id) => axiosInstance.delete(`/students/${id}/`),
};

// ─── TEACHERS ──────────────────────────────────────────────────
export const teacherService = {
  list: (params) => axiosInstance.get('/teachers/', { params }),
  get: (id) => axiosInstance.get(`/teachers/${id}/`),
  create: (data) => axiosInstance.post('/teachers/', data),
  update: (id, data) => axiosInstance.patch(`/teachers/${id}/`, data),
  delete: (id) => axiosInstance.delete(`/teachers/${id}/`),
};

// ─── CLASSES ───────────────────────────────────────────────────
export const classService = {
  list: (params) => axiosInstance.get('/classes/', { params }),
  get: (id) => axiosInstance.get(`/classes/${id}/`),
  create: (data) => axiosInstance.post('/classes/', data),
  update: (id, data) => axiosInstance.patch(`/classes/${id}/`, data),
  delete: (id) => axiosInstance.delete(`/classes/${id}/`),
};

// ─── SECTIONS ──────────────────────────────────────────────────
export const sectionService = {
  list: (params) => axiosInstance.get('/sections/', { params }),
  get: (id) => axiosInstance.get(`/sections/${id}/`),
  create: (data) => axiosInstance.post('/sections/', data),
  update: (id, data) => axiosInstance.patch(`/sections/${id}/`, data),
  delete: (id) => axiosInstance.delete(`/sections/${id}/`),
};

// ─── SUBJECTS ──────────────────────────────────────────────────
export const subjectService = {
  list: (params) => axiosInstance.get('/subjects/', { params }),
  get: (id) => axiosInstance.get(`/subjects/${id}/`),
  create: (data) => axiosInstance.post('/subjects/', data),
  update: (id, data) => axiosInstance.patch(`/subjects/${id}/`, data),
  delete: (id) => axiosInstance.delete(`/subjects/${id}/`),
};

// ─── ATTENDANCE ────────────────────────────────────────────────
export const attendanceService = {
  list: (params) => axiosInstance.get('/attendance/', { params }),
  create: (data) => axiosInstance.post('/attendance/', data),
  bulkCreate: (data) => axiosInstance.post('/attendance/bulk_create/', data),
  update: (id, data) => axiosInstance.patch(`/attendance/${id}/`, data),
};

// ─── EXAMINATIONS ──────────────────────────────────────────────
export const examService = {
  list: (params) => axiosInstance.get('/examinations/', { params }),
  get: (id) => axiosInstance.get(`/examinations/${id}/`),
  create: (data) => axiosInstance.post('/examinations/', data),
  update: (id, data) => axiosInstance.patch(`/examinations/${id}/`, data),
  delete: (id) => axiosInstance.delete(`/examinations/${id}/`),
};

// ─── MARKS ─────────────────────────────────────────────────────
export const marksService = {
  list: (params) => axiosInstance.get('/marks/', { params }),
  create: (data) => axiosInstance.post('/marks/', data),
  update: (id, data) => axiosInstance.patch(`/marks/${id}/`, data),
};

// ─── RESULTS ───────────────────────────────────────────────────
export const resultService = {
  list: (params) => axiosInstance.get('/results/', { params }),
  get: (id) => axiosInstance.get(`/results/${id}/`),
};

// ─── FEES ──────────────────────────────────────────────────────
export const feeService = {
  list: (params) => axiosInstance.get('/fees/', { params }),
  get: (id) => axiosInstance.get(`/fees/${id}/`),
  create: (data) => axiosInstance.post('/fees/', data),
  update: (id, data) => axiosInstance.patch(`/fees/${id}/`, data),
};

// ─── ANNOUNCEMENTS ─────────────────────────────────────────────
export const announcementService = {
  list: (params) => axiosInstance.get('/announcements/', { params }),
  get: (id) => axiosInstance.get(`/announcements/${id}/`),
  create: (data) => axiosInstance.post('/announcements/', data),
  update: (id, data) => axiosInstance.patch(`/announcements/${id}/`, data),
  delete: (id) => axiosInstance.delete(`/announcements/${id}/`),
};

// ─── ASSIGNMENTS ───────────────────────────────────────────────
export const assignmentService = {
  list: (params) => axiosInstance.get('/assignments/', { params }),
  get: (id) => axiosInstance.get(`/assignments/${id}/`),
  create: (data) => axiosInstance.post('/assignments/', data, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
  submit: (data) => axiosInstance.post('/submissions/', data, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
};

// ─── TIMETABLE ─────────────────────────────────────────────────
export const timetableService = {
  list: (params) => axiosInstance.get('/timetable/', { params }),
  create: (data) => axiosInstance.post('/timetable/', data),
  update: (id, data) => axiosInstance.patch(`/timetable/${id}/`, data),
  delete: (id) => axiosInstance.delete(`/timetable/${id}/`),
};

// ─── ACTIVITY LOGS ─────────────────────────────────────────────
export const activityLogService = {
  list: (params) => axiosInstance.get('/logs/', { params }),
};
