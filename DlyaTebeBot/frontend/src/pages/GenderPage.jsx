import { useParams } from "react-router-dom";
import { useDispatch, useSelector } from "react-redux";

import { fetchBrandsByCategory, fetchProductsByCategory, resetHomeProducts } from "../store/productsSlice";

import CategoryItem from "../components/CategoryItem";
import ProductsListLayout from "../components/ProductsListLayout";
import { useEffect } from "react";

const GenderPage = () => {
  const { slug } = useParams();
  const dispatch = useDispatch();

  const productsState = useSelector((state) => state.products);

  const {
    brandsByCategory = [],
    categoryProducts = [],
    categoryNext = null,
    status = "idle",
  } = productsState || {};


  useEffect(() => {
    dispatch(fetchBrandsByCategory({ slug }));
    dispatch(resetHomeProducts());
    dispatch(fetchProductsByCategory({ slug }));
  }, [dispatch, slug]);

  const applyFilters = () => {
      dispatch(resetHomeProducts());
      dispatch(fetchProductsByCategory({ slug }));
    };

  const brandList = Array.isArray(brandsByCategory)
    ? brandsByCategory
    : brandsByCategory?.results || [];

  return (
    <div className="pt-4">
      <div className="grid grid-cols-4 md:grid-cols-5 lg:grid-cols-6 gap-4 mb-10">
        {brandList.map((brand) => (
          <CategoryItem
            key={brand.id}
            category={brand}
            link="brand"
          />
        ))}
      </div>

      <ProductsListLayout
        products={categoryProducts}
        next={categoryNext}
        status={status}
        onApplyFilters={applyFilters}
        onLoadMore={() =>
          dispatch(fetchProductsByCategory({ slug, url: next }))
        }
      />
    </div>
  );
};

export default GenderPage;
