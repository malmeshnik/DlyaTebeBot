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
    params,
  } = productState || {}

  useEffect(() => {
    dispatch(resetHomeProducts());
    dispatch(fetchProductsByBrand({slug}));
  }, [params, dispatch, slug]);

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
          dispatch(fetchProductsByBrand({ slug, url: brandNext }))
        }
      />
    </div>
  );
};

export default BrandPage;
