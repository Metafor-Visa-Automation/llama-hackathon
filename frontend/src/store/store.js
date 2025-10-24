import { configureStore } from '@reduxjs/toolkit';
import countryReducer from './countrySlice';
import authReducer from './authSlice';

export const store = configureStore({
  reducer: {
    country: countryReducer,
    auth: authReducer,
  },
});

