import { Link } from "react-router-dom";

const ProductCard = ({ product }) => {

  return (
    <Link
      to={`/product/${product.slug}`}
      className="
        relative rounded-xl overflow-hidden bg-white shadow-xl
        flex flex-col transition hover:scale-[1.02]
      "
    >
      {/* IMAGE */}
      <div className="p-3 rounded-xl bg-gray-200">
        <div className="bg-white rounded-xl p-4 flex items-center justify-center">
          <img
            src={product.image}
            alt={product.name}
            className="max-h-32 object-contain"
          />
        </div>
      </div>

      {/* INFO */}
      <div className="p-3 flex-1">
        <h3 className="text-base md:text-lg font-bold">
          {product.name}
        </h3>

        <div className="flex items-center gap-2">
          {product.old_price && (
            <p className="text-gray-400 line-through text-sm">
              {product.old_price} zł
            </p>
          )}
          <p
            className={
              product.old_price
                ? "text-red-600 font-bold"
                : "text-gray-600"
            }
          >
            {product.price} zł
          </p>
        </div>
      </div>

    </Link>
  );
};

export default ProductCard;
