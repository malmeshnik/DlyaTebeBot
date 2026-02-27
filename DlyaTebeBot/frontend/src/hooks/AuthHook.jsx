import { useEffect } from "react";

const useTelegramAuth = () => {
  useEffect(() => {
    const tg = window.Telegram.WebApp;

    fetch("/api/telegram-auth/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        initData: tg.initData
      })
    })
      .then(res => res.json())
      .then(data => {
        localStorage.setItem("access", data.access);
        localStorage.setItem("refresh", data.refresh);
      });
  }, []);
};

export default useTelegramAuth;