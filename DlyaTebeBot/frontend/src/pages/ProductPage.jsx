import { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useParams } from 'react-router-dom';
import { fetchProduct } from '../store/productsSlice';

import ProductGallery from '../components/ProductGallery';

const ProductPage = () => {
  const { slug } = useParams();
  const dispatch = useDispatch();

  const { status } = useSelector((state) => state.products);
  const product = useSelector((state) => state.products.currentProduct);

  // Завантаження товару
  useEffect(() => {
    dispatch(fetchProduct(slug));
  }, [dispatch, slug]);

  // Поки вантажиться
  if (status === "loading" || !product) {
    return <p className="text-center text-gray-500 mt-6">Завантаження...</p>;
  }

  // Формуємо галерею
  const galleryImages = [{ image: product.image }];

  return (
    <div className="mt-6">
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-10">

        {/* LEFT — ГАЛЕРЕЯ */}
        <div className="bg-white rounded-xl shadow-sm p-4">
          <ProductGallery images={galleryImages} />
        </div>

        {/* RIGHT — ІНФО */}
        <div className="bg-white rounded-xl shadow-sm p-6 flex flex-col justify-between">

          {/* Назва */}
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              {product.name}
            </h1>

            {/* Ціна */}
            <div className="mt-4 flex items-center gap-3">
              {product.old_price && (
                <span className="text-gray-400 line-through text-xl">
                  {product.old_price} zł
                </span>
              )}

              <span className="text-3xl text-red-600 font-bold">
                {product.price} zł
              </span>
            </div>

            {/* Доступність */}
            {product.available !== undefined && (
              <p className="mt-2 text-gray-600 text-lg">
                <span className="font-semibold">Доступно:</span> {product.available} шт
              </p>
            )}


            {/* Характеристики */}
            {product.characteristics && (
              <div className="mt-6">
                <h2 className="text-xl font-semibold mb-3">Характеристики</h2>
                <p className="text-gray-700 leading-relaxed whitespace-pre-line">
                  {product.characteristics}
                </p>
              </div>
            )}
          </div>

        </div>
      </div>

      {/* ОПИС */}
      {product.description && (
        <div className="mt-10 bg-white rounded-xl shadow-sm p-6">
          <h2 className="text-2xl font-semibold mb-4">Описание товара</h2>
          <p className="text-gray-700 leading-relaxed">
            {product.description}
          </p>
        </div>
      )}
    </div>
  );
};

export default ProductPage;
