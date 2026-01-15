import React from 'react';

const ProductGallery = ({ images }) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {images && images.map((image) => (
        <img
          key={image.image}   // УНІКАЛЬНИЙ та завжди існуючий ключ
          src={image.image}
          alt="Product"
          className="w-full h-auto object-cover rounded-lg"
        />
      ))}
    </div>
  );
};

export default ProductGallery;
