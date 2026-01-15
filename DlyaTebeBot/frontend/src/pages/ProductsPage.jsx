import { useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";


import { fetchProducts, resetHomeProducts } from "../store/productsSlice";

import FilterSortBar from "../components/filterSortBar";
import ProductCard from "../components/productCard";

const ProductsPage = ({ filters = {}, children }) => {
  const dispatch = useDispatch();

  const { products, next, status } = useSelector(
    (state) => state.products
  );

  const productsList = Array.isArray(products)
    ? products
    : products?.results || [];

  if (!productsList.length) return null;

  // =======================
  // INITIAL LOAD
  // =======================
  useEffect(() => {
    dispatch(resetHomeProducts());
    dispatch(fetchProducts(filters));
  }, [dispatch, JSON.stringify(filters)]);

  // =======================
  // INFINITE SCROLL
  // =======================
  useEffect(() => {
    const onScroll = () => {
      if (
        window.innerHeight + window.scrollY >=
          document.body.offsetHeight - 300 &&
        status !== "loading" &&
        next
      ) {
        dispatch(fetchProducts({ url: next }));
      }
    };

    window.addEventListener("scroll", onScroll);
    return () => window.removeEventListener("scroll", onScroll);
  }, [dispatch, next, status]);

  // =======================
  // APPLY FILTERS / SORT
  // =======================
  const applyFilters = () => {
    dispatch(resetHomeProducts());
    dispatch(fetchProducts(filters));
  };

  return (
    <>
      {children}

      <FilterSortBar onApply={applyFilters} />

      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 mt-4">
        {products.map((product) => (
          <ProductCard key={product.id} product={product} />
        ))}
      </div>

      {status === "loading" && (
        <p className="text-center my-4 text-gray-500">
          Завантаження...
        </p>
      )}
    </>
  );
};

export default ProductsPage;
