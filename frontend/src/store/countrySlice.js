import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  originCountry: { code: 'TR', name: 'Türkiye' }, // Default to Turkey
  destinationCountry: null, // Will store { code: 'FR', name: 'Fransa' }
  startDate: null,
  endDate: null,
  applicationType: '',
};

const countrySlice = createSlice({
  name: 'country',
  initialState,
  reducers: {
    setOriginCountry: (state, action) => {
      state.originCountry = action.payload;
    },
    setDestinationCountry: (state, action) => {
      // Payload should be an object with { code, name }
      state.destinationCountry = action.payload;
    },
    setStartDate: (state, action) => {
      state.startDate = action.payload;
    },
    setEndDate: (state, action) => {
      state.endDate = action.payload;
    },
    setApplicationType: (state, action) => {
      state.applicationType = action.payload;
    },
    resetCountries: (state) => {
      state.originCountry = { code: 'TR', name: 'Türkiye' };
      state.destinationCountry = null;
      state.startDate = null;
      state.endDate = null;
      state.applicationType = '';
    },
  },
});

export const { 
  setOriginCountry, 
  setDestinationCountry, 
  setStartDate,
  setEndDate,
  setApplicationType,
  resetCountries 
} = countrySlice.actions;
export default countrySlice.reducer;

