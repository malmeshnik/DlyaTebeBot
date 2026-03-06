import { useEffect } from "react";

const useMiniAppAuth = (onDone) => {
  useEffect(() => {
    const tg = window.Telegram?.WebApp;

    // TELEGRAM AUTH
    if (tg?.initData) {
      fetch("/api/miniapp/telegram-auth/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ initData: tg.initData }),
      })
        .then((res) => res.json())
        .then((data) => {
          localStorage.setItem("access", data.access);
          localStorage.setItem("refresh", data.refresh);
          localStorage.setItem("telegram_id", data.user.telegram_id);

          onDone?.(null);
        })
        .catch((err) => {
          console.error(err);
          onDone?.("Помилка Telegram авторизації");
        });

      return;
    }

    const params = new URLSearchParams(window.location.search);

    const miniapp_token = params.get("token");

    if (miniapp_token) {
      fetch("/api/miniapp/viber-auth/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ token: miniapp_token }),
      })
        .then((res) => res.json())
        .then((data) => {
          localStorage.setItem("access", data.access);
          localStorage.setItem("refresh", data.refresh);
          localStorage.setItem("viber_id", data.user.viber_id);

          onDone?.(null);
        })
        .catch((err) => {
          console.error(err);
          onDone?.("Помилка Viber авторизації");
        });

      return;
    }

    onDone?.("Невідома платформа авторизації");
  }, []);
};

export default useMiniAppAuth;