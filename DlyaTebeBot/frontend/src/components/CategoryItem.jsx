import { Link } from "react-router-dom";

const CategoryItem = ({ category }) => {
    return (
        <Link
            to={`/category/${category.slug}`}
            key={category.id}
            className="flex flex-col items-center"
            >
            <div
                className="
                w-full 
                aspect-square 
                rounded-xl 
                bg-gray-100 
                overflow-hidden 
                shadow-sm
                md:w-24 md:h-24
                lg:w-28 lg:h-28
                "
            >
                {category.image && (
                <img
                    src={category.image}
                    alt={category.name}
                    className="w-full h-full object-cover"
                />
                )}
            </div>

            <p
                className="
                mt-2 
                text-center 
                text-[11px] 
                md:text-sm 
                lg:text-base 
                font-semibold
                "
            >
                {category.name}
            </p>
        </Link>
    );
}

export default CategoryItem