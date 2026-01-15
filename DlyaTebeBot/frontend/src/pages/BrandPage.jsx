import { useParams } from "react-router-dom";
import ProductsPage from "./ProductsPage";

const BrandPage = () => {
  const { slug } = useParams();

  return (
    <ProductsPage filters={{ brand: slug }} />
  );
};

export default BrandPage;
