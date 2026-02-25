import { BrowserRouter, Routes, Route } from "react-router-dom";

import HomePage from "./pages/HomePage";
import GenderPage from "./pages/GenderPage"
import BrandPage from "./pages/BrandPage";
import ProductPage from "./pages/ProductPage";
import Layout from "./components/Layout";

const App = () => {
  return (
    <BrowserRouter basename="/miniapp">
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

      </Routes>
    </BrowserRouter>
  );
};

export default App;
