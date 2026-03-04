import { useState } from "react";
import { createPortal } from "react-dom";

import api from "../api/client";

const BuyButton = ({ productId, variantId }) => {
  const [isLoading, setIsLoading] = useState(false);
  const [showModal, setShowModal] = useState(false);

  const handleBuy = async () => {
    try {
      setIsLoading(true);

      console.log("SENDING:", {
        product_id: productId,
        variant_id: variantId || null,
      });

      await api.post("orders/create_order/", {
        product_id: productId,
        variant_id: variantId || null,
      });

      setShowModal(true);

    } catch (err) {
      console.error("Order error:", err);

      let errorMessage = "Сталася невідома помилка. Спробуйте ще раз.";

      alert(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      <button
        className="w-full bg-black text-white py-2 rounded-xl font-semibold transition hover:bg-gray-800 active:scale-95 disabled:opacity-50"
        onClick={handleBuy}
        disabled={isLoading}
      >
        {isLoading ? "Обробка..." : "Купити"}
      </button>

      {showModal &&
        createPortal(
          <div className="fixed inset-0 z-[9999] flex items-center justify-center">
            {/* overlay */}
            <div
              className="absolute inset-0 bg-black/50"
              onClick={() => setShowModal(false)}
            />

            {/* modal */}
            <div className="relative bg-white rounded-2xl p-6 max-w-sm w-full text-center shadow-2xl animate-fadeIn">
              <h2 className="text-xl font-bold mb-3">
                Дякуємо за замовлення!
              </h2>
              <p className="text-gray-600 mb-6">
                Наш менеджер скоро звʼяжеться з вами.
              </p>
              <button
                className="w-full bg-black text-white py-2 rounded-xl font-semibold hover:bg-gray-800 transition"
                onClick={() => setShowModal(false)}
              >
                Окей
              </button>
            </div>
          </div>,
          document.body
        )}
    </>
  );
};

export default BuyButton;