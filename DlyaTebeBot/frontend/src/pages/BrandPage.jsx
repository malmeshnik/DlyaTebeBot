import { useParams } from "react-router-dom";
import { useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";

import { fetchProductsByBrand, resetHomeProducts } from "../store/productsSlice";

import ProductsListLayout from "../components/ProductsListLayout";


const BrandPage = () => {
  const { slug } = useParams();
  const dispatch = useDispatch();

  const productState = useSelector((state) => state.products)

  const {
    brandProducts = [],
    brandNext = null,
    status = "idle",
  } = productState || {}

  useEffect(() => {
    dispatch(resetHomeProducts());
    dispatch(fetchProductsByBrand({slug}));
  }, [dispatch, slug]);

  const applyFilters = () => {
    dispatch(resetHomeProducts());
    dispatch(fetchProductsByBrand({slug}));
  }

  return (
    <div className="pt-4">
      <ProductsListLayout
        products={brandProducts}
        next={brandNext}
        status={status}
        onApplyFilters={applyFilters}
        onLoadMore={() =>
          dispatch(fetchProductsByCategory({ slug, url: next }))
        }
      />
    </div>
  );
};

export default BrandPage;
