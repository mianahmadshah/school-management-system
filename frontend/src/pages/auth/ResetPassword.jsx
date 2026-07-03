import React from 'react';

const ResetPassword = () => {
  return (
    <div className="flex items-center justify-center min-h-screen bg-blue-50">
      <form className="bg-white p-8 rounded shadow-md w-full max-w-sm">
        <h2 className="text-2xl font-bold mb-6 text-center">Reset Password</h2>
        {/* New Password */}
        <div className="mb-4">
          <label className="block mb-1 font-semibold">New Password</label>
          <input type="password" className="w-full px-3 py-2 border rounded" required />
        </div>
        {/* Confirm Password */}
        <div className="mb-4">
          <label className="block mb-1 font-semibold">Confirm Password</label>
          <input type="password" className="w-full px-3 py-2 border rounded" required />
        </div>
        {/* Submit */}
        <button type="submit" className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700">Reset Password</button>
      </form>
    </div>
  );
};

export default ResetPassword;
