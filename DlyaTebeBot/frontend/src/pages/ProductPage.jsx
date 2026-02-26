import { useEffect, useState, useMemo } from "react";
import { useDispatch, useSelector } from "react-redux";
import { useParams } from "react-router-dom";
import { fetchProduct } from "../store/productsSlice";

import ProductGallery from "../components/ProductGallery";
import BuyButton from "../components/BuyButton";

const ProductPage = () => {
  const { slug } = useParams();
  const dispatch = useDispatch();

  const { status } = useSelector((state) => state.products);
  const product = useSelector((state) => state.products.currentProduct);

  const hasVariants = product?.variants?.length > 0;

  const [selectedVariantId, setSelectedVariantId] = useState(null);

  useEffect(() => {
    dispatch(fetchProduct(slug));
  }, [dispatch, slug]);

  // Коли продукт завантажився → вибираємо перший варіант
  useEffect(() => {
    if (product?.variants?.length > 0) {
      setSelectedVariantId(product.variants[0].id);
    }
  }, [product]);

  const selectedVariant = useMemo(() => {
    if (!hasVariants) return null;
    return product.variants.find(v => v.id === selectedVariantId);
  }, [selectedVariantId, product, hasVariants]);

  if (status === "loading" || !product) {
    return <p className="text-center text-gray-500 mt-6">Завантаження...</p>;
  }

  const displayPrice = selectedVariant?.price || product.price;
  const displayOldPrice = selectedVariant?.old_price || product.old_price;

  const galleryImages = [{ image: product.image }];

  return (
    <div className="mt-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-10">

        {/* LEFT — ГАЛЕРЕЯ */}
        <div className="bg-white rounded-xl shadow-sm p-4">
          <ProductGallery images={galleryImages} />
        </div>

        {/* RIGHT — ІНФО */}
        <div className="bg-white rounded-xl shadow-sm p-6 flex flex-col">

          {product.brand?.name && (
            <p className="text-xl uppercase tracking-wide text-gray-500 mb-1">
              {product.brand.name}
            </p>
          )}

          <h1 className="text-3xl font-bold text-gray-900">
            {product.name}
          </h1>

          {/* VARIANTS */}
          {hasVariants && (
            <div className="flex gap-3 flex-wrap mt-6">
              {product.variants.map((variant) => (
                <button
                  key={variant.id}
                  type="button"
                  onClick={() => setSelectedVariantId(variant.id)}
                  className={`
                    px-4 py-2 rounded-full border transition text-sm
                    ${
                      selectedVariantId === variant.id
                        ? "bg-black text-white border-black"
                        : "bg-white text-gray-700 border-gray-300 hover:border-black"
                    }
                  `}
                >
                  {variant.volume_ml} ml
                </button>
              ))}
            </div>
          )}

          {/* PRICE */}
          <div className="mt-6 flex items-center gap-4">
            {displayOldPrice && (
              <span className="text-gray-400 line-through text-xl">
                {displayOldPrice} грн.
              </span>
            )}

            <span className="text-3xl text-red-600 font-bold">
              {displayPrice} грн.
            </span>
          </div>

          <BuyButton
            productId={product.id}
            variantId={selectedVariant?.id}
          />

          {/* DESCRIPTION */}
          {product.characteristics && (
            <div className="mt-8">
              <h2 className="text-xl font-semibold mb-3">Опис</h2>
              <p className="text-gray-700 leading-relaxed whitespace-pre-line">
                {product.characteristics}
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ProductPage;