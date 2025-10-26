import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  checklistData: null, // Will store the API response
  isLoading: false,
  error: null,
};

const visaChecklistSlice = createSlice({
  name: 'visaChecklist',
  initialState,
  reducers: {
    setChecklistLoading: (state, action) => {
      state.isLoading = action.payload;
    },
    setChecklistData: (state, action) => {
      state.checklistData = action.payload;
      state.isLoading = false;
      state.error = null;
    },
    setChecklistError: (state, action) => {
      state.error = action.payload;
      state.isLoading = false;
    },
    resetChecklist: (state) => {
      state.checklistData = null;
      state.isLoading = false;
      state.error = null;
    },
  },
});

export const {
  setChecklistLoading,
  setChecklistData,
  setChecklistError,
  resetChecklist,
} = visaChecklistSlice.actions;

export default visaChecklistSlice.reducer;
