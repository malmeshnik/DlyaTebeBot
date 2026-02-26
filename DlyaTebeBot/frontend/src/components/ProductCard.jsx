import { Link } from "react-router-dom";
import { useState, useMemo } from "react";

import BuyButton from "./BuyButton";

const ProductCard = ({ product }) => {
  const hasVariants = product.variants?.length > 0;

  const [selectedVariantId, setSelectedVariantId] = useState(
    hasVariants ? product.variants[0].id : null
  );

  const selectedVariant = useMemo(() => {
    if (!hasVariants) return null;
    return product.variants.find(v => v.id === selectedVariantId);
  }, [selectedVariantId, product.variants]);

  const displayPrice = selectedVariant?.price || product.price;
  const displayOldPrice = selectedVariant?.old_price || product.old_price;

  return (
    <>
      <div className="rounded-xl bg-white shadow-xl flex flex-col h-full transition hover:scale-[1.02] hover:shadow-2xl p-4">
  
      <Link to={`/product/${product.slug}`} className="flex justify-center mb-3">
        <img
          src={product.image}
          alt={product.name}
          className="max-h-28 object-contain transition duration-300 hover:scale-105"
        />
      </Link>

      {hasVariants && (
        <div className="flex gap-2 flex-wrap justify-center mb-3">
          {product.variants.map((variant) => (
            <button
              key={variant.id}
              type="button"
              onClick={() => setSelectedVariantId(variant.id)}
              className={`px-3 py-1 rounded-full text-sm border transition ${
                selectedVariantId === variant.id
                  ? "bg-black text-white border-black"
                  : "bg-white text-gray-700 border-gray-300 hover:border-black"
              }`}
            >
              {variant.volume_ml} ml
            </button>
          ))}
        </div>
      )}

      <div className="flex flex-col flex-1">

        {product.brand?.name && (
          <p className="text-xs uppercase tracking-wide text-gray-400 mb-1 text-center">
            {product.brand.name}
          </p>
        )}

        <Link to={`/product/${product.slug}`}>
          <h3 className="text-base md:text-lg font-bold leading-snug mb-1 text-center hover:underline">
            {product.name}
          </h3>
        </Link>

        {product.characteristics && (
          <p className="text-sm text-gray-600 line-clamp-3 mb-3 text-center">
            {product.characteristics}
          </p>
        )}

        <div className="flex justify-center items-center gap-2 mb-4">
          {displayOldPrice && (
            <p className="text-sm text-gray-400 line-through">
              {displayOldPrice} грн.
            </p>
          )}
          <p
            className={
              displayOldPrice
                ? "text-red-600 font-bold text-lg"
                : "text-gray-800 font-semibold text-lg"
            }
          >
            {displayPrice} грн.
          </p>
        </div>

        <div className="mt-auto">
          <BuyButton
            productId={product.id}
            variantId={selectedVariant?.id}
          />
        </div>

      </div>
    </div>

    </>
  );
};

export default ProductCard;