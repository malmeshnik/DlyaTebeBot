import { useState, useEffect, useMemo } from "react";
import { useDispatch, useSelector } from "react-redux";
import {
  setParams,
  fetchBrandsByCategory,
  fetchModelsByBrand,
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

  const modelsByBrand = useMemo(() => {
    const data = productsState?.modelsByBrand;
    if (Array.isArray(data)) return data;
    if (Array.isArray(data?.results)) return data.results;
    return [];
  }, [productsState?.modelsByBrand]);

  const [open, setOpen] = useState(false);

  // FILTER STATE
  const [category, setCategory] = useState("");
  const [brand, setBrand] = useState("");
  const [model, setModel] = useState("");
  const [ordering, setOrdering] = useState("");
  const [priceMin, setPriceMin] = useState("");
  const [priceMax, setPriceMax] = useState("");

  /* =======================
     CATEGORY → BRANDS
  ======================= */
  useEffect(() => {
    if (!category) return;

    dispatch(fetchBrandsByCategory(category));
    setBrand("");
    setModel("");

    dispatch(
      setParams({
        category,
        brand: null,
        model: null,
      })
    );
  }, [category, dispatch]);

  /* =======================
     BRAND → MODELS
  ======================= */
  useEffect(() => {
    if (!brand) return;

    dispatch(fetchModelsByBrand(brand));
    setModel("");

    dispatch(
      setParams({
        brand,
        model: null,
      })
    );
  }, [brand, dispatch]);

  /* =======================
     APPLY
  ======================= */
  const apply = () => {
    dispatch(
      setParams({
        model: model || null,
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
    setCategory("");
    setBrand("");
    setModel("");
    setOrdering("");
    setPriceMin("");
    setPriceMax("");

    dispatch(
      setParams({
        category: null,
        brand: null,
        model: null,
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
          ⚙️ Фильтры
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
          <option value="">По умолчанию</option>
          <option value="price">От дешевых к дорогим</option>
          <option value="-price">От дорогих к дешевым</option>
        </select>
      </div>

      {/* MODAL */}
      {open && (
        <div className="fixed inset-0 z-40 bg-black/40">
          <div className="absolute bottom-0 w-full bg-white rounded-t-2xl p-5 max-h-[90vh] overflow-y-auto">
            <h3 className="text-xl font-bold mb-4">Фильтры</h3>

            {/* CATEGORY */}
            <div className="mb-4">
              <label className="block font-semibold mb-1">Категория</label>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="w-full p-2 border rounded-lg"
              >
                <option value="">Все категории</option>
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
                  <option value="">Все бренды</option>
                  {brandsByCategory.map((b) => (
                    <option key={b.slug} value={b.slug}>
                      {b.name}
                    </option>
                  ))}
                </select>
              </div>
            )}

            {/* MODEL */}
            {modelsByBrand.length > 0 && (
              <div className="mb-4">
                <label className="block font-semibold mb-1">Модель</label>
                <select
                  value={model}
                  onChange={(e) => setModel(e.target.value)}
                  className="w-full p-2 border rounded-lg"
                >
                  <option value="">Все модели</option>
                  {modelsByBrand.map((m) => (
                    <option key={m.slug} value={m.slug}>
                      {m.name}
                    </option>
                  ))}
                </select>
              </div>
            )}

            {/* PRICE */}
            <div className="mb-4">
              <label className="block font-semibold mb-1">Цена</label>
              <div className="flex gap-3">
                <input
                  type="number"
                  placeholder="От"
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
                Применить
              </button>

              <button
                onClick={reset}
                className="flex-1 py-3 rounded-lg bg-gray-100 font-semibold"
              >
                Сбросить
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default FilterSortBar;
