import { createSlice } from '@reduxjs/toolkit';

// Load auth state from localStorage
const loadAuthFromStorage = () => {
  try {
    const token = localStorage.getItem('authToken');
    const user = localStorage.getItem('authUser');
    const tokenExpiration = localStorage.getItem('tokenExpiration');

    if (token && user) {
      // Check if token is expired
      if (tokenExpiration && new Date().getTime() > parseInt(tokenExpiration)) {
        // Token expired, clear storage
        localStorage.removeItem('authToken');
        localStorage.removeItem('authUser');
        localStorage.removeItem('tokenExpiration');
        return {
          isAuthenticated: false,
          user: null,
          token: null,
          tokenExpiration: null,
        };
      }

      return {
        isAuthenticated: true,
        user: JSON.parse(user),
        token: token,
        tokenExpiration: tokenExpiration ? parseInt(tokenExpiration) : null,
      };
    }
  } catch (error) {
    console.error('Error loading auth from localStorage:', error);
  }

  return {
    isAuthenticated: false,
    user: null,
    token: null,
    tokenExpiration: null,
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

      // Calculate token expiration time (current time + expires_in seconds)
      const expiresIn = action.payload.expiresIn || 3600; // Default 1 hour if not provided
      const expirationTime = new Date().getTime() + (expiresIn * 1000);
      state.tokenExpiration = expirationTime;

      // Save to localStorage
      localStorage.setItem('authToken', action.payload.token);
      localStorage.setItem('authUser', JSON.stringify(action.payload.user));
      localStorage.setItem('tokenExpiration', expirationTime.toString());
    },
    logout: (state) => {
      state.isAuthenticated = false;
      state.user = null;
      state.token = null;
      state.tokenExpiration = null;

      // Clear localStorage
      localStorage.removeItem('authToken');
      localStorage.removeItem('authUser');
      localStorage.removeItem('tokenExpiration');
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

