import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  originCountry: 'TR', // Default to Turkey
  destinationCountry: null, // Will store { code: 'FR', name: 'Fransa' }
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
    resetCountries: (state) => {
      state.originCountry = 'TR';
      state.destinationCountry = null;
    },
  },
});

export const { setOriginCountry, setDestinationCountry, resetCountries } = countrySlice.actions;
export default countrySlice.reducer;

