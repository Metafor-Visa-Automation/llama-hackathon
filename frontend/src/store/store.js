import { configureStore } from '@reduxjs/toolkit';
import countryReducer from './countrySlice';
import authReducer from './authSlice';
import formReducer from './formSlice';
import applicationReducer from './applicationSlice';
import dashboardReducer from './dashboardSlice';


export const store = configureStore({
  reducer: {
    country: countryReducer,
    auth: authReducer,
    form: formReducer,
    application: applicationReducer,
    dashboard: dashboardReducer,
  },
});

