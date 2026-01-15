import {
  Link,
  Outlet,
  useLocation,
  useNavigate,
} from "react-router-dom";
import { useSelector, useDispatch } from "react-redux";
import { setSearchTerm } from "../store/searchSlice";

import {
  HomeIcon,
  MagnifyingGlassIcon,
  ArrowLeftIcon,
} from "@heroicons/react/24/outline";

const Layout = () => {
  const dispatch = useDispatch();

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
              <button
                onClick={goBack}
                className="flex items-center"
              >
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
                placeholder="Поиск..."
                className="w-full bg-gray-100 text-black
                  pl-10 pr-4 py-2 rounded-xl
                  focus:outline-none focus:ring-2 focus:ring-gray-300"
                onChange={(e) =>
                  dispatch(setSearchTerm(e.target.value))
                }
              />
            </div>
          </div>
        </div>
      </nav>

      {/* ================= CONTENT ================= */}
      <main className="max-w-6xl mx-auto p-4">
        <Outlet />
      </main>
    </div>
  );
};

export default Layout;
