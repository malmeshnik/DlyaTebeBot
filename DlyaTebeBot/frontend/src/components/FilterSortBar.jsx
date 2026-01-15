import { useState, useEffect, useMemo } from "react";
import { useDispatch, useSelector } from "react-redux";
import {
  setParams,
  fetchBrandsByCategory,
} from "../store/productsSlice";

const FilterSortBar = ({ onApply }) => {
  const dispatch = useDispatch();

  const productsState = useSelector((state) => state.products);

  const categories = useMemo(() => {
    const data = productsState?.categories;
    if (Array.isArray(data)) return data;
    if (Array.isArray(data?.results)) return data.results;
    return [];
  }, [productsState?.categories]);

  const brandsByCategory = useMemo(() => {
    const data = productsState?.brandsByCategory;
    if (Array.isArray(data)) return data;
    if (Array.isArray(data?.results)) return data.results;
    return [];
  }, [productsState?.brandsByCategory]);

  const [open, setOpen] = useState(false);

  // FILTER STATE
  const [gender, setGender] = useState("");
  const [brand, setBrand] = useState("");
  const [ordering, setOrdering] = useState("");
  const [priceMin, setPriceMin] = useState("");
  const [priceMax, setPriceMax] = useState("");

  /* =======================
     CATEGORY → BRANDS
  ======================= */
  useEffect(() => {
    if (!gender) return;

    dispatch(fetchBrandsByCategory(gender));
    setBrand("");

    dispatch(
      setParams({
        gender,
        brand: null,
      })
    );
  }, [gender, dispatch]);

  /* =======================
     APPLY
  ======================= */
  const apply = () => {
    dispatch(
      setParams({
        ordering: ordering || null,
        price_min: priceMin || null,
        price_max: priceMax || null,
      })
    );

    setOpen(false);
    onApply?.();
  };

  /* =======================
     RESET
  ======================= */
  const reset = () => {
    setGender("");
    setBrand("");
    setOrdering("");
    setPriceMin("");
    setPriceMax("");

    dispatch(
      setParams({
        gender: null,
        brand: null,
        ordering: null,
        price_min: null,
        price_max: null,
      })
    );

    setOpen(false);
    onApply?.();
  };

  return (
    <>
      {/* TOP BAR */}
      <div className="sticky top-[64px] z-30 bg-white border-b px-4 py-3 flex justify-between">
        <button
          onClick={() => setOpen(true)}
          className="px-4 py-2 rounded-lg border text-sm font-semibold"
        >
          ⚙️ Фільтри
        </button>

        <select
          value={ordering}
          onChange={(e) => {
            const value = e.target.value || "";
            setOrdering(value);
            dispatch(setParams({ ordering: value || null }));
            onApply?.();
          }}
          className="px-3 py-2 border rounded-lg text-sm"
        >
          <option value="">За замовчуванням</option>
          <option value="price">Від дешевих до дорогих</option>
          <option value="-price">Від дорогих до дешевих</option>
        </select>
      </div>

      {/* MODAL */}
      {open && (
        <div className="fixed inset-0 z-40 bg-black/40">
          <div className="absolute bottom-0 w-full bg-white rounded-t-2xl p-5 max-h-[90vh] overflow-y-auto">
            <h3 className="text-xl font-bold mb-4">Фільтри</h3>

            {/* CATEGORY */}
            <div className="mb-4">
              <label className="block font-semibold mb-1">Для кого</label>
              <select
                value={gender}
                onChange={(e) => setGender(e.target.value)}
                className="w-full p-2 border rounded-lg"
              >
                <option value="">Всі види</option>
                {categories.map((c) => (
                  <option key={c.slug} value={c.slug}>
                    {c.name}
                  </option>
                ))}
              </select>
            </div>

            {/* BRAND */}
            {brandsByCategory.length > 0 && (
              <div className="mb-4">
                <label className="block font-semibold mb-1">Бренд</label>
                <select
                  value={brand}
                  onChange={(e) => setBrand(e.target.value)}
                  className="w-full p-2 border rounded-lg"
                >
                  <option value="">Всі бренди</option>
                  {brandsByCategory.map((b) => (
                    <option key={b.slug} value={b.slug}>
                      {b.name}
                    </option>
                  ))}
                </select>
              </div>
            )}

            {/* PRICE */}
            <div className="mb-4">
              <label className="block font-semibold mb-1">Ціна</label>
              <div className="flex gap-3">
                <input
                  type="number"
                  placeholder="Від"
                  value={priceMin}
                  onChange={(e) => setPriceMin(e.target.value)}
                  className="flex-1 p-2 border rounded-lg"
                />
                <input
                  type="number"
                  placeholder="До"
                  value={priceMax}
                  onChange={(e) => setPriceMax(e.target.value)}
                  className="flex-1 p-2 border rounded-lg"
                />
              </div>
            </div>

            {/* ACTIONS */}
            <div className="flex gap-3 mt-6">
              <button
                onClick={apply}
                className="flex-1 py-3 rounded-lg bg-black text-white font-semibold"
              >
                Застосувати
              </button>

              <button
                onClick={reset}
                className="flex-1 py-3 rounded-lg bg-gray-100 font-semibold"
              >
                Скинути
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default FilterSortBar;
