import { Link, Outlet, useLocation, useNavigate } from "react-router-dom";
import { useDispatch } from "react-redux";
import { useState, useEffect, useCallback } from "react";

import {
  HomeIcon,
  MagnifyingGlassIcon,
  ArrowLeftIcon,
} from "@heroicons/react/24/outline";
import { setParams } from "../store/productsSlice";
import useMiniAppAuth from "../hooks/useMiniAppAuth";

const Layout = () => {
  const dispatch = useDispatch();
  const [search, setSearch] = useState("");
  const [authError, setAuthError] = useState(null);
  const [isAuthReady, setIsAuthReady] = useState(false);

  const handleAuthDone = useCallback((error) => {
    if (error) setAuthError(error);
    setIsAuthReady(true);
  }, []);

  useMiniAppAuth(handleAuthDone);

  useEffect(() => {
    const t = setTimeout(() => {
      dispatch(setParams({ search: search || null }));
    }, 300);

    return () => clearTimeout(t);
  }, [search, dispatch]);

  const location = useLocation();
  const navigate = useNavigate();

  const isHome = location.pathname === "/";

  const goBack = () => {
    if (window.history.length > 1) {
      navigate(-1);
    } else {
      navigate("/");
    }
  };

  return (
    <div className="min-h-screen bg-white relative pb-20">
      {/* ================= AUTH ERROR NOTIFICATION ================= */}
      {authError && (
        <div className="fixed top-0 left-0 right-0 bg-red-500 text-white p-4 text-center z-50">
          {authError}
        </div>
      )}

      {/* ================= NAVBAR ================= */}
      <nav className="w-full py-3 px-4 border-b bg-white sticky top-0 z-50">
        <div className="max-w-6xl mx-auto flex items-center justify-between gap-3">
          {/* LEFT ICON */}
          <div className="min-w-[44px] flex items-center">
            {isHome ? (
              <Link to="/" className="flex items-center">
                <HomeIcon className="w-7 h-7 text-black" />
              </Link>
            ) : (
              <button onClick={goBack} className="flex items-center">
                <ArrowLeftIcon className="w-7 h-7 text-black" />
              </button>
            )}
          </div>

          {/* SEARCH */}
          <div className="flex-1 mx-3">
            <div className="relative">
              <MagnifyingGlassIcon className="absolute left-3 top-2.5 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="Пошук..."
                className="w-full bg-gray-100 text-black pl-10 pr-4 py-2 rounded-xl focus:outline-none focus:ring-2 focus:ring-gray-300"
                onChange={(e) =>
                  dispatch(setParams({ search: e.target.value || null }))
                }
              />
            </div>
          </div>
        </div>
      </nav>

      {/* ================= CONTENT ================= */}
      <main className="max-w-6xl mx-auto p-4">
        {isAuthReady ? (
          <Outlet />
        ) : (
          <div className="flex items-center justify-center h-40 text-gray-400">
            Завантаження...
          </div>
        )}
      </main>
    </div>
  );
};

export default Layout;