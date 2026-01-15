import { useParams } from "react-router-dom";
import ProductsPage from "./ProductsPage";

const CategoryPage = () => {
  const { slug } = useParams();

  return (
    <ProductsPage filters={{ category: slug }} />
  );
};

export default CategoryPage;
