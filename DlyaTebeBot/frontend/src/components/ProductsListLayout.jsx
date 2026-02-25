import { useEffect } from "react";
import FilterSortBar from "./FilterSortBar";
import ProductCard from "./ProductCard";

const ProductsListLayout = ({
  products = [],
  next,
  status,
  onLoadMore,
  onApplyFilters,
}) => {
  // =======================
  // INFINITE SCROLL
  // =======================
  useEffect(() => {
    const onScroll = () => {
      if (
        window.innerHeight + window.scrollY >=
          document.body.offsetHeight - 400 &&
        status !== "loading" &&
        next
      ) {
        onLoadMore();
      }
    };

    window.addEventListener("scroll", onScroll);
    return () => window.removeEventListener("scroll", onScroll);
  }, [next, status, onLoadMore]);

  return (
    <>
      <FilterSortBar onApply={onApplyFilters} />

      {status === "loading" && products.length === 0 && (
        <p className="text-center">Завантаження...</p>
      )}

      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 mt-4">
        {products.map((product) => (
          <ProductCard key={product.id} product={product} />
        ))}
      </div>

      {status === "loading" && products.length > 0 && (
        <p className="text-center mt-6">
          Завантажуємо ще...
        </p>
      )}
    </>
  );
};

export default ProductsListLayout;
