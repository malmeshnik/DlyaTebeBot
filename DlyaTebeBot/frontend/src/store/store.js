import { configureStore } from "@reduxjs/toolkit";
import productsReducer from "./productsSlice";
import serchReducer from "./searchSlice";

export const store = configureStore({
  reducer: {
    products: productsReducer,
    search: serchReducer,
  },
});
