import { useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";

import {
  fetchCategories,
  fetchProducts,
  resetHomeProducts,
} from "../store/productsSlice";

import BannerSlider from "../components/BannerSlider";
import CategoryItem from "../components/CategoryItem";
import ProductsListLayout from "../components/ProductsListLayout";

const HomePage = () => {
  const dispatch = useDispatch();

  const {
    categories,
    products,
    next,
    status,
  } = useSelector((state) => state.products);

  // =======================
  // INITIAL LOAD
  // =======================
  useEffect(() => {
    dispatch(fetchCategories());
    dispatch(resetHomeProducts());
    dispatch(fetchProducts({}));
  }, [dispatch]);

  // =======================
  // APPLY FILTERS / SORT
  // =======================
  const applyFilters = () => {
    dispatch(resetHomeProducts());
    dispatch(fetchProducts({}));
  };

  // =======================
  // NORMALIZE CATEGORIES
  // =======================
  const categoryList = Array.isArray(categories)
    ? categories
    : categories?.results || [];

  return (
    <div className="pt-4">
      <BannerSlider />

      {/* =======================
          CATEGORIES
      ======================= */}
      <div className="grid grid-cols-4 md:grid-cols-5 lg:grid-cols-6 gap-4 mb-10">
        {categoryList.map((category) => (
          <CategoryItem
            key={category.id}
            category={category}
          />
        ))}
      </div>

      {/* =======================
          PRODUCTS
      ======================= */}
      <ProductsListLayout
        products={products}
        next={next}
        status={status}
        onApplyFilters={applyFilters}
        onLoadMore={() =>
          dispatch(fetchProducts({ url: next }))
        }
      />
    </div>
  );
};

export default HomePage;
