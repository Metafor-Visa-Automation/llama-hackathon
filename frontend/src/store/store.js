import { configureStore } from '@reduxjs/toolkit';
import countryReducer from './countrySlice';
import authReducer from './authSlice';
import formReducer from './formSlice';

export const store = configureStore({
  reducer: {
    country: countryReducer,
    auth: authReducer,
    form: formReducer,
  },
});

