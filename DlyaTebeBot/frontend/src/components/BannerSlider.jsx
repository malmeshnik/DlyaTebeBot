import React, { useEffect, useState } from "react";
import Slider from "react-slick";
import api from "../api/client";

import "slick-carousel/slick/slick.css"; 
import "slick-carousel/slick/slick-theme.css";

const BannerSlider = () => {
  const [banners, setBanners] = useState([]);
  const [loading, setLoading] = useState(true);

  const bannerList = Array.isArray(banners)
    ? banners
    : banners?.results || [];

  if (!bannerList.length) return null;

  useEffect(() => {
    const fetchBanners = async () => {
      try {
        const response = await api.get("/banners/");
        // якщо бекенд повертає { results: [...] }
        setBanners(response.data.results || response.data || []);
        console.log("Banners:", response.data);
      } catch (err) {
        console.error("Помилка завантаження банерів", err);
      } finally {
        setLoading(false);
      }
    };

    fetchBanners();
  }, []);

  if (loading) return <p className="text-center my-4 text-gray-500">Завантаження банерів...</p>;
  if (!banners.length) return null;

  const settings = {
    dots: true,
    infinite: banners.length > 1,
    speed: 500,
    slidesToShow: 1,
    slidesToScroll: 1,
    arrows: false,
    autoplay: banners.length > 1,
    autoplaySpeed: 5000,
  };

  return (
    <div className="mb-6">
      <Slider {...settings}>
        {banners.map((banner) => (
          <div key={banner.id} className="relative">
            {banner.link ? (
              <a href={banner.link} target="_blank" rel="noopener noreferrer">
                <img
                  src={banner.image}
                  alt={banner.title || `Banner ${banner.id}`}
                  className="w-full h-48 md:h-64 lg:h-80 object-cover rounded-xl"
                />
              </a>
            ) : (
              <img
                src={banner.image}
                alt={banner.title || `Banner ${banner.id}`}
                className="w-full h-48 md:h-64 lg:h-80 object-cover rounded-xl"
              />
            )}
          </div>
        ))}
      </Slider>
    </div>
  );
};

export default BannerSlider;
