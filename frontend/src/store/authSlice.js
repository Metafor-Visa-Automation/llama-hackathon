import { createSlice } from '@reduxjs/toolkit';

// Load auth state from localStorage
const loadAuthFromStorage = () => {
  try {
    const token = localStorage.getItem('authToken');
    const user = localStorage.getItem('authUser');
    
    if (token && user) {
      return {
        isAuthenticated: true,
        user: JSON.parse(user),
        token: token,
      };
    }
  } catch (error) {
    console.error('Error loading auth from localStorage:', error);
  }
  
  return {
    isAuthenticated: false,
    user: null,
    token: null,
  };
};

const initialState = loadAuthFromStorage();

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    loginSuccess: (state, action) => {
      state.isAuthenticated = true;
      state.user = action.payload.user;
      state.token = action.payload.token;
      
      // Save to localStorage
      localStorage.setItem('authToken', action.payload.token);
      localStorage.setItem('authUser', JSON.stringify(action.payload.user));
    },
    logout: (state) => {
      state.isAuthenticated = false;
      state.user = null;
      state.token = null;
      
      // Clear localStorage
      localStorage.removeItem('authToken');
      localStorage.removeItem('authUser');
    },
    updateUser: (state, action) => {
      state.user = { ...state.user, ...action.payload };
      
      // Update user in localStorage
      if (state.user) {
        localStorage.setItem('authUser', JSON.stringify(state.user));
      }
    },
  },
});

export const { loginSuccess, logout, updateUser } = authSlice.actions;
export default authSlice.reducer;

