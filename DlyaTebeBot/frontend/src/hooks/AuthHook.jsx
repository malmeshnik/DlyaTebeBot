import { useEffect } from "react";

const useTelegramAuth = (onDone) => {
  useEffect(() => {
    const tg = window.Telegram?.WebApp;

    if (!tg?.initData) {
      onDone?.("Не вдалося отримати дані Telegram");
      return;
    }

    fetch("/api/miniapp/telegram-auth/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ initData: tg.initData }),
    })
      .then((res) => {
        if (!res.ok) throw new Error(`Помилка авторизації: ${res.status}`);
        return res.json();
      })
      .then((data) => {
        localStorage.setItem("access", data.access);
        localStorage.setItem("refresh", data.refresh);

        localStorage.setItem(
          "telegram_id",
          String(data.user.telegram_id)
        );

        onDone?.(null);
      })
      .catch((error) => {
        console.error("Authentication error:", error);
        onDone?.(error.message || "Помилка авторизації");
      });
  }, []);
};

export default useTelegramAuth;