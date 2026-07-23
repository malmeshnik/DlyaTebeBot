import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const TelegramStartHandler = ({ children }) => {
  const navigate = useNavigate();

  useEffect(() => {
    const tg = window.Telegram?.WebApp;

    if (tg?.initDataUnsafe?.start_param) {
      const startParam = tg.initDataUnsafe.start_param;

      // Якщо параметр bonus_wheel - редиректимо на колесо
      if (startParam === 'bonus_wheel') {
        navigate('/bonus-wheel');
      }
    }
  }, [navigate]);

  return children;
};

export default TelegramStartHandler;
