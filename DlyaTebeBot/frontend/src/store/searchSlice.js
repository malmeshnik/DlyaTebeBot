import { createSlice } from "@reduxjs/toolkit";

const searchSlice = createSlice({
  name: "search",
  initialState: {
    term: "",
  },
  reducers: {
    setSearchTerm(state, action) {
      state.term = action.payload;
    },
    clearSearch(state) {
      state.term = "";
    }
  }
});

export const { setSearchTerm, clearSearch } = searchSlice.actions;
export default searchSlice.reducer;
