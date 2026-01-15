import { BrowserRouter, Routes, Route } from "react-router-dom";

import HomePage from "./pages/HomePage";
import CategoryPage from "./pages/CategoryPage";
import BrandPage from "./pages/BrandPage";

const App = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HomePage />} />

        <Route
          path="/category/:slug"
          element={<CategoryPage />}
        />

        <Route
          path="/brand/:slug"
          element={<BrandPage />}
        />

      </Routes>
    </BrowserRouter>
  );
};

export default App;
