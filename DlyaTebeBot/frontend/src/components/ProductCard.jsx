import { Link } from "react-router-dom";

const ProductCard = ({ product }) => {
  return (
    <Link
      to={`/product/${product.slug}`}
      className="
        relative rounded-xl overflow-hidden bg-white shadow-xl
        flex flex-col transition
        hover:scale-[1.02] hover:shadow-2xl
      "
    >
      {/* IMAGE */}
      <div className="p-3 rounded-xl bg-gray-200">
        <div className="bg-white rounded-xl p-4 flex items-center justify-center">
          <img
            src={product.image}
            alt={product.name}
            className="max-h-32 object-contain transition group-hover:scale-105"
          />
        </div>
      </div>

      {/* INFO */}
      <div className="p-3 flex-1 flex flex-col">
        {/* BRAND */}
        {product.brand?.name && (
          <p className="text-xs uppercase tracking-wide text-gray-400 mb-1">
            {product.brand.name}
          </p>
        )}

        {/* NAME */}
        <h3 className="text-base md:text-lg font-bold leading-snug line-clamp-2">
          {product.name}
        </h3>

        {/* DESCRIPTION */}
        {product.characteristics && (
          <p className="text-sm text-gray-500 mt-1 line-clamp-2">
            {product.characteristics}
          </p>
        )}

        {/* PRICE */}
        <div className="mt-auto pt-3 flex items-center gap-2">
          {product.old_price && (
            <p className="text-sm text-gray-400 line-through">
              {product.old_price} грн.
            </p>
          )}
          <p
            className={
              product.old_price
                ? "text-red-600 font-bold text-lg"
                : "text-gray-700 font-semibold text-lg"
            }
          >
            {product.price} грн.
          </p>
        </div>
      </div>
    </Link>
  );
};

export default ProductCard;
