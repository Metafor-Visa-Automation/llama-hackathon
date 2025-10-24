import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  originCountry: 'TR', // Default to Turkey
  destinationCountry: null,
};

const countrySlice = createSlice({
  name: 'country',
  initialState,
  reducers: {
    setOriginCountry: (state, action) => {
      state.originCountry = action.payload;
    },
    setDestinationCountry: (state, action) => {
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

