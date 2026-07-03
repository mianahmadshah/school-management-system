import { create } from 'zustand';
import { persist } from 'zustand/middleware';

const useAuthStore = create(
  persist(
    (set) => ({
      user: null, // { id, email, role, full_name, profile_picture }
      accessToken: null,
      refreshToken: null,
      
      // Actions
      login: (user, accessToken, refreshToken) => set({
        user,
        accessToken,
        refreshToken
      }),
      
      setAccessToken: (token) => set({ accessToken: token }),
      
      logout: () => set({
        user: null,
        accessToken: null,
        refreshToken: null
      }),
      
      updateUser: (userData) => set((state) => ({
        user: { ...state.user, ...userData }
      })),
    }),
    {
      name: 'sms-auth-storage', // name of the item in the storage (must be unique)
      // By default, it uses localStorage which is perfect for auth
    }
  )
);

export default useAuthStore;
