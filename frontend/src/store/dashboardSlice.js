import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { getApplications } from '../services/dashboardService';

export const fetchApplications = createAsyncThunk(
  'dashboard/fetchApplications',
  async (_, { getState, rejectWithValue }) => {
    try {
      const token = getState().auth.token;
      if (!token) {
        return rejectWithValue('No auth token found');
      }
      const response = await getApplications(token);
      return response;
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

const dashboardSlice = createSlice({
  name: 'dashboard',
  initialState: {
    applications: [],
    status: 'idle', // 'idle' | 'loading' | 'succeeded' | 'failed'
    error: null,
  },
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchApplications.pending, (state) => {
        state.status = 'loading';
        state.error = null;
      })
      .addCase(fetchApplications.fulfilled, (state, action) => {
        state.status = 'succeeded';
        state.applications = action.payload;
      })
      .addCase(fetchApplications.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.payload;
      });
  },
});

export const selectDashboard = (state) => state.dashboard;
export default dashboardSlice.reducer;
