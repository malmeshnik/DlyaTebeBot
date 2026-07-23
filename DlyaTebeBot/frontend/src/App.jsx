import { BrowserRouter, Routes, Route } from "react-router-dom";

import HomePage from "./pages/HomePage";
import GenderPage from "./pages/GenderPage"
import BrandPage from "./pages/BrandPage";
import ProductPage from "./pages/ProductPage";
import BonusWheel from "./pages/BonusWheel";
import Layout from "./components/Layout";
import TelegramStartHandler from "./components/TelegramStartHandler";

const App = () => {
  return (
    <BrowserRouter basename="/miniapp">
      <TelegramStartHandler>
        <Routes>
          <Route element={<Layout />}>
            <Route path="/" element={<HomePage />} />

            <Route
              path="/gender/:slug"
              element={<GenderPage />}
            />

            <Route
              path="/brand/:slug"
              element={<BrandPage />}
            />

            <Route
              path="/product/:slug"
              element={<ProductPage />}
            />
          </Route>

          {/* Колесо фортуни без Layout */}
          <Route path="/bonus-wheel" element={<BonusWheel />} />

        </Routes>
      </TelegramStartHandler>
    </BrowserRouter>
  );
};

export default App;
