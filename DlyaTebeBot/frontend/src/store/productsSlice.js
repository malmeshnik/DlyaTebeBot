import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import api from "../api/client";

// =======================
// HELPERS
// =======================

// normalize next url from DRF pagination
const normalizeNextUrl = (url) => {
  if (!url) return null;

  try {
    const parsed = new URL(url, window.location.origin);
    let path = parsed.pathname + parsed.search;

    if (path.startsWith("/api/miniapp/")) {
      path = path.replace("/api/miniapp", "");
    }

    return path;
  } catch {
    return url;
  }
};

// 🔥 remove empty params before request
const cleanParams = (params) =>
  Object.fromEntries(
    Object.entries(params).filter(
      ([_, value]) =>
        value !== null && value !== "" && value !== undefined
    )
  );

// =======================
// INITIAL STATE
// =======================

const initialState = {
  // HOME
  products: [],
  next: null,

  // CATEGORY
  categoryProducts: [],
  categoryNext: null,
  brandsByCategory: [],

  // BRAND
  brandProducts: [],
  brandNext: null,

  // META
  categories: [],
  brands: [],
  currentProduct: null,

  // 🔥 FILTERS (ONLY USER-SELECTED)
  params: {
    price_min: null,
    price_max: null,
    ordering: null,
    search: null,
  },

  status: "idle",
  error: null,
};

// =======================
// THUNKS
// =======================

// ---------- HOME ----------

export const fetchProducts = createAsyncThunk(
  "products/fetchProducts",
  async ({ url = null }, { getState }) => {
    console.log("🚀 FETCH PRODUCTS START");
    const { params } = getState().products;

    const requestUrl = url
      ? normalizeNextUrl(url)
      : "/products/";

    const response = await api.get(requestUrl, {
      params: cleanParams(params),
    });

    return {
      results: response.data.results,
      next: response.data.next,
      initial: !url,
    };
  }
);

// ---------- CATEGORIES ----------
export const fetchCategories = createAsyncThunk(
  "products/fetchCategories",
  async () => {
    const response = await api.get("/genders/");
    return response.data;
  }
);

// ---------- ALL BRANDS ----------
export const fetchBrands = createAsyncThunk(
  "products/fetchBrands",
  async () => {
    const response = await api.get("/brands/");
    return response.data;
  }
);

// ---------- BRANDS BY CATEGORY ----------
export const fetchBrandsByCategory = createAsyncThunk(
  "products/fetchBrandsByCategory",
  async (slug) => {
    const response = await api.get("/brands/", {
      params: {
        gender: slug,
      },
    });

    return response.data.results ?? response.data;
  }
);

// ---------- PRODUCT DETAIL ----------
export const fetchProduct = createAsyncThunk(
  "products/fetchProduct",
  async (slug) => {
    const response = await api.get(`/products/${slug}/`);
    return response.data;
  }
);

// ---------- CATEGORY PRODUCTS ----------
export const fetchProductsByCategory = createAsyncThunk(
  "products/fetchProductsByCategory",
  async ({ slug, url = null }, { getState }) => {
    const { params } = getState().products;

    const requestUrl = url
      ? normalizeNextUrl(url)
      : "/products/";

    const response = await api.get(requestUrl, {
      params: {
        gender: slug,
        ...cleanParams(params),
      },
    });

    return {
      results: response.data.results,
      next: response.data.next,
      initial: !url,
    };
  }
);

// ---------- BRAND PRODUCTS ----------
export const fetchProductsByBrand = createAsyncThunk(
  "products/fetchProductsByBrand",
  async ({ slug, url = null }, { getState }) => {
    const { params } = getState().products;

    const requestUrl = url
      ? normalizeNextUrl(url)
      : "/products/";

    const response = await api.get(requestUrl, {
      params: {
        brand: slug,               // 🔥 brand ONLY from URL
        ...cleanParams(params),    // 🔥 model / price / ordering
      },
    });

    return {
      results: response.data.results,
      next: response.data.next,
      initial: !url,
    };
  }
);

// =======================
// SLICE
// =======================

const productsSlice = createSlice({
  name: "products",
  initialState,

  reducers: {
    // 🔥 UPDATE FILTERS (ONLY WHAT USER SET)
    setParams: (state, action) => {
      state.params = {
        ...state.params,
        ...action.payload,
      };
    },

    // RESET CATEGORY
    resetCategoryProducts: (state) => {
      state.categoryProducts = [];
      state.categoryNext = null;
    },

    // RESET BRAND
    resetBrandProducts: (state) => {
      state.brandProducts = [];
      state.brandNext = null;
      state.modelsByBrand = [];   // 🔥 reset models
      state.params.model = null; // 🔥 reset selected model
    },

    // RESET HOME
    resetHomeProducts: (state) => {
      state.products = [];
      state.next = null;
    },
  },

  extraReducers: (builder) => {
    builder
      // HOME
      .addCase(fetchProducts.pending, (state) => {
        state.status = "loading";
      })
      .addCase(fetchProducts.fulfilled, (state, action) => {
        state.status = "succeeded";
        action.payload.initial
          ? (state.products = action.payload.results)
          : state.products.push(...action.payload.results);
        state.next = action.payload.next;
      })

      // CATEGORIES
      .addCase(fetchCategories.fulfilled, (state, action) => {
        state.categories = action.payload;
      })

      // BRANDS
      .addCase(fetchBrands.fulfilled, (state, action) => {
        state.brands = action.payload;
      })

      // BRANDS BY CATEGORY
      .addCase(fetchBrandsByCategory.fulfilled, (state, action) => {
        state.brandsByCategory = action.payload;
      })

      // PRODUCT DETAIL
      .addCase(fetchProduct.pending, (state) => {
        state.status = "loading";
        state.currentProduct = null;
      })
      .addCase(fetchProduct.fulfilled, (state, action) => {
        state.status = "succeeded";
        state.currentProduct = action.payload;
      })

      // CATEGORY PRODUCTS
      .addCase(fetchProductsByCategory.pending, (state) => {
        state.status = "loading";
      })
      .addCase(fetchProductsByCategory.fulfilled, (state, action) => {
        state.status = "succeeded";
        action.payload.initial
          ? (state.categoryProducts = action.payload.results)
          : state.categoryProducts.push(...action.payload.results);
        state.categoryNext = action.payload.next;
      })

      // BRAND PRODUCTS
      .addCase(fetchProductsByBrand.pending, (state) => {
        state.status = "loading";
      })
      .addCase(fetchProductsByBrand.fulfilled, (state, action) => {
        state.status = "succeeded";
        action.payload.initial
          ? (state.brandProducts = action.payload.results)
          : state.brandProducts.push(...action.payload.results);
        state.brandNext = action.payload.next;
      });
  },
});

// =======================
// EXPORTS
// =======================

export const {
  setParams,
  resetCategoryProducts,
  resetBrandProducts,
  resetHomeProducts,
} = productsSlice.actions;

export default productsSlice.reducer;
