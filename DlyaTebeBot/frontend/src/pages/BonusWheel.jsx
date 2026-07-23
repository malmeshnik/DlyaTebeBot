import { useEffect, useState, useRef } from 'react';
import styles from './BonusWheel.module.css';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

const BonusWheel = () => {
  const [prizes, setPrizes] = useState([]);
  const [isSpinning, setIsSpinning] = useState(false);
  const [hasSpun, setHasSpun] = useState(false); // "1 спін на людину" — кнопка стає CTA в бот
  const [currentSpinResult, setCurrentSpinResult] = useState(null);
  const [alreadySpun, setAlreadySpun] = useState(false);
  const [previousSpin, setPreviousSpin] = useState(null);

  // Модалка: три окремі стани, щоб відтворити ефект "проявляється з диму"
  // (фон темніє одразу, а сам блок з призом матеріалізується із затримкою)
  const [modalShow, setModalShow] = useState(false);
  const [modalDark, setModalDark] = useState(false);
  const [modalMaterialize, setModalMaterialize] = useState(false);

  const [totalRotation, setTotalRotation] = useState(0);
  const [isTelegram, setIsTelegram] = useState(false);

  const wrRef = useRef(null);
  const svgRef = useRef(null);
  const ringRef = useRef(null);
  const containerRef = useRef(null);
  const stageRef = useRef(null);
  const capRef = useRef(null);
  const dropRef = useRef(null);
  const bottleRef = useRef(null);

  const NS = "http://www.w3.org/2000/svg";
  const cx = 280, cy = 280;
  const R1 = 260, R0 = 100, rc = 16;
  const gap = 1.2;

  useEffect(() => {
    // Перевіряємо чи це Telegram
    const tg = window.Telegram?.WebApp;
    if (tg?.initData) {
      setIsTelegram(true);
      tg.expand();
      tg.ready();
    }

    // Завантажуємо призи
    fetchPrizes();
    // Перевіряємо eligibility
    checkEligibility();
  }, []);

  // fix: розмір сцени (zoom) має рахуватись одразу при монтуванні,
  // а не лише після завантаження призів — інакше на повільному
  // з'єднанні колесо може "стрибнути" в розмірі вже після появи
  useEffect(() => {
    resizeStage();
    window.addEventListener('resize', resizeStage);
    const onOrientation = () => setTimeout(resizeStage, 50);
    window.addEventListener('orientationchange', onOrientation);

    return () => {
      window.removeEventListener('resize', resizeStage);
      window.removeEventListener('orientationchange', onOrientation);
    };
  }, []);

  useEffect(() => {
    if (prizes.length > 0) {
      drawWheel();
    }
  }, [prizes]);

  const fetchPrizes = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/miniapp/wheel/prizes/`);
      const data = await response.json();
      setPrizes(data);
    } catch (error) {
      console.error('Помилка завантаження призів:', error);
    }
  };

  const checkEligibility = async () => {
    try {
      const token = localStorage.getItem('access');
      const sessionKey = localStorage.getItem('wheel_session');

      const headers = {
        'Content-Type': 'application/json',
      };

      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const url = sessionKey
        ? `${API_BASE_URL}/api/miniapp/wheel/check-eligibility/?session_key=${sessionKey}`
        : `${API_BASE_URL}/api/miniapp/wheel/check-eligibility/`;

      const response = await fetch(url, { headers });
      const data = await response.json();

      if (data.already_spun) {
        setAlreadySpun(true);
        setPreviousSpin({
          prize: data.prize,
          code: data.code
        });
      }
    } catch (error) {
      console.error('Помилка перевірки eligibility:', error);
    }
  };

  const drawWheel = () => {
    if (!svgRef.current || prizes.length === 0) return;

    const svg = svgRef.current;
    svg.innerHTML = '';

    const N = prizes.length;
    const step = 360 / N;

    // Створюємо defs для градієнта
    const defs = document.createElementNS(NS, 'defs');
    const grad = document.createElementNS(NS, 'linearGradient');
    grad.id = 'rg';
    grad.setAttribute('gradientUnits', 'userSpaceOnUse');
    grad.setAttribute('x1', '120');
    grad.setAttribute('y1', '40');
    grad.setAttribute('x2', '440');
    grad.setAttribute('y2', '520');

    [['0%', 0.92], ['45%', 0.48], ['100%', 0.08]].forEach(([offset, opacity]) => {
      const stop = document.createElementNS(NS, 'stop');
      stop.setAttribute('offset', offset);
      stop.setAttribute('stop-color', `rgba(255,255,255,${opacity})`);
      grad.appendChild(stop);
    });

    defs.appendChild(grad);
    svg.appendChild(defs);

    // Малюємо сектори
    prizes.forEach((prize, i) => {
      const a0 = i * step + gap / 2;
      const a1 = (i + 1) * step - gap / 2;
      const mid = (a0 + a1) / 2;
      const d = path(a0, a1);

      // Сегмент (div з clip-path)
      const seg = document.createElement('div');
      seg.className = styles.segment;
      seg.style.clipPath = `path("${d.replace(/\s+/g, ' ')}")`;
      seg.style.background = createSegmentGradient(prize.color);
      seg.style.filter = 'drop-shadow(0 5px 12px rgba(60,40,30,0.16))';
      wrRef.current?.insertBefore(seg, svg);

      // Контур
      const rim = document.createElementNS(NS, 'path');
      rim.setAttribute('d', d);
      rim.setAttribute('fill', 'none');
      rim.setAttribute('stroke', 'url(#rg)');
      rim.setAttribute('stroke-width', '2.8');
      rim.setAttribute('stroke-linejoin', 'round');
      svg.appendChild(rim);

      // Блик
      const [hx, hy] = polar((R1 + R0) / 2 - 5, a0 + (a1 - a0) * 0.32);
      const shine = document.createElementNS(NS, 'ellipse');
      shine.setAttribute('cx', hx);
      shine.setAttribute('cy', hy);
      shine.setAttribute('rx', '36');
      shine.setAttribute('ry', '20');
      shine.setAttribute('transform', `rotate(${mid + 15} ${hx} ${hy})`);
      shine.setAttribute('fill', 'rgba(255,255,255,0.52)');
      shine.setAttribute('filter', 'blur(12px)');
      svg.appendChild(shine);

      // Текст призу
      const [lx, ly] = polar((R0 + R1) / 2 + 8, mid);
      const label = document.createElementNS(NS, 'text');
      label.setAttribute('x', lx);
      label.setAttribute('y', ly);
      label.setAttribute('text-anchor', 'middle');
      label.setAttribute('dominant-baseline', 'middle');
      label.setAttribute('font-size', '23');
      label.setAttribute('font-weight', '700');
      label.setAttribute('font-family', "-apple-system, 'Segoe UI', sans-serif");
      label.setAttribute('fill', '#4a4038');
      label.setAttribute('stroke', 'rgba(255,255,255,0.65)');
      label.setAttribute('stroke-width', '4');
      label.setAttribute('paint-order', 'stroke');
      // fix: без корекції текст у нижній половині кола (mid від 90° до 270°)
      // рендериться догори ногами, бо rotate(mid) просто повторює кут сектора.
      // Довертаємо такі підписи ще на 180° НАВКОЛО ЇХНЬОЇ Ж точки опори (lx, ly) —
      // це не зсуває текст, а лише розвертає його на читабельний бік.
      const textRotate = (mid > 90 && mid < 270) ? mid + 180 : mid;
      label.setAttribute('transform', `rotate(${textRotate} ${lx} ${ly})`);
      label.setAttribute('data-sector', i);
      // fix: раніше весь напис призу йшов ОДНИМ рядком (label.textContent =
      // prize.name), тому довгі назви ("Тестер з улюбленим парфумом") просто
      // вилазили за межі сектора величезним нечитабельним рядком. Тепер
      // розбиваємо назву на слова і рахуємо, скільки слів влазить у ширину
      // сектора (по хорді на середньому радіусі) — слова, що не влізли,
      // переносяться на наступний рядок через <tspan>. Самі слова НІКОЛИ не
      // розбиваються по буквах, лише переносяться цілими.
      const words = prize.name.split(' ').filter(Boolean);
      const midRadius = (R0 + R1) / 2;
      const maxWidthPx = midRadius * rad(step) * 0.82;
      const avgCharWidth = 23 * 0.56; // емпірична оцінка ширини символу для bold 23px
      const maxCharsPerLine = Math.max(3, Math.floor(maxWidthPx / avgCharWidth));

      const lines = [];
      let currentLine = '';
      words.forEach((word) => {
        const candidate = currentLine ? `${currentLine} ${word}` : word;
        if (candidate.length > maxCharsPerLine && currentLine) {
          lines.push(currentLine);
          currentLine = word;
        } else {
          currentLine = candidate;
        }
      });
      if (currentLine) lines.push(currentLine);

      const lineHeight = 24;
      const startDy = -((lines.length - 1) * lineHeight) / 2;
      lines.forEach((line, li) => {
        const tspan = document.createElementNS(NS, 'tspan');
        tspan.setAttribute('x', lx);
        tspan.setAttribute('dy', li === 0 ? startDy : lineHeight);
        tspan.textContent = line;
        label.appendChild(tspan);
      });
      // Повну назву призу зберігаємо окремо в data-атрибуті — вона потрібна
      // для порівняння з переможним призом в animate(), а textContent тепер
      // складається з кількох tspan-рядків без пробілів між ними.
      label.setAttribute('data-prize-name', prize.name);
      svg.appendChild(label);
    });

    // Лампочки
    const ring = ringRef.current;
    if (ring) {
      ring.innerHTML = '';
      for (let i = 0; i < 32; i++) {
        const [x, y] = polar(298, (i / 32) * 360);
        const l = document.createElement('div');
        l.className = styles.light;
        l.style.left = `${x}px`;
        l.style.top = `${y}px`;
        l.style.animationDelay = `${i * 0.06}s`;
        ring.appendChild(l);
      }
    }

    // Показуємо сцену лише після того, як браузер порахував фінальний
    // layout — прибирає "битий" перший кадр без підписів на секторах
    requestAnimationFrame(() => {
      void stageRef.current?.offsetHeight; 
      requestAnimationFrame(() => stageRef.current?.classList.add(styles.ready));
    });
  };

  // fix: раніше сектор просто заливався кольором з бекенду з різною
  // прозорістю (${hexColor}dd/cc/dd) — колір лишався тим самим, мінявся
  // лише альфа-канал поверх бежового фону сторінки. Через це сектори
  // виглядали пласкими/вицвілими, без того "скляного" об'єму, що був на
  // початковій сторінці.
  // На початковій сторінці ефект досягався варіюванням САМЕ ЯСКРАВОСТІ
  // (lightness) в HSL при незмінних hue/saturation: світліше в центрі
  // (90%) → темніше на середині (76%) → знову світліше на краю (83%).
  // Тут беремо hue і saturation з кольору, що прийшов з бекенду
  // (конвертуючи hex → HSL), і застосовуємо ту саму формулу яскравості —
  // сектори лишаються "тим кольором, який задав бекенд", але отримують
  // назад той самий об'ємний ефект.
  const hexToHsl = (hex) => {
    let h = hex.replace('#', '');
    if (h.length === 3) h = h.split('').map((c) => c + c).join('');
    const r = parseInt(h.substring(0, 2), 16) / 255;
    const g = parseInt(h.substring(2, 4), 16) / 255;
    const b = parseInt(h.substring(4, 6), 16) / 255;
    const max = Math.max(r, g, b), min = Math.min(r, g, b);
    let hue = 0, sat = 0;
    const light = (max + min) / 2;
    if (max !== min) {
      const d = max - min;
      sat = light > 0.5 ? d / (2 - max - min) : d / (max + min);
      switch (max) {
        case r: hue = (g - b) / d + (g < b ? 6 : 0); break;
        case g: hue = (b - r) / d + 2; break;
        case b: hue = (r - g) / d + 4; break;
        default: break;
      }
      hue /= 6;
    }
    return { h: hue * 360, s: sat * 100 };
  };

  const hslStr = (h, s, l, a) => `hsla(${h},${s}%,${l}%,${a})`;

  const createSegmentGradient = (hexColor) => {
    const { h, s } = hexToHsl(hexColor || '#d4af37');
    const inner = hslStr(h, s, 90, 0.85);
    const md = hslStr(h, s, 76, 0.85);
    const outer = hslStr(h, s, 83, 0.85);
    return `linear-gradient(135deg, rgba(255,255,255,0.28), transparent 52%), radial-gradient(circle at ${cx}px ${cy}px, ${inner} ${R0}px, ${md} ${(R0 + R1) / 2}px, ${outer} ${R1}px)`;
  };

  const rad = (d) => d * Math.PI / 180;

  const polar = (r, d) => {
    const a = rad(d - 90);
    return [cx + r * Math.cos(a), cy + r * Math.sin(a)];
  };

  const pt = (p) => `${p[0].toFixed(1)},${p[1].toFixed(1)}`;

  const path = (a0, a1) => {
    const d1 = Math.min((rc / R1) * 57.3, (a1 - a0) / 2 - 0.5);
    const d0 = Math.min((rc / R0) * 57.3, (a1 - a0) / 2 - 0.5);

    const V1 = polar(R1, a0), V2 = polar(R1, a1);
    const V3 = polar(R0, a1), V4 = polar(R0, a0);

    const P1 = polar(R1, a0 + d1), P2 = polar(R1, a1 - d1);
    const P3 = polar(R1 - rc, a1), P4 = polar(R0 + rc, a1);
    const P5 = polar(R0, a1 - d0), P6 = polar(R0, a0 + d0);
    const P7 = polar(R0 + rc, a0), P8 = polar(R1 - rc, a0);

    return `M${pt(P1)} A${R1} ${R1} 0 0 1 ${pt(P2)} Q${pt(V2)} ${pt(P3)} L${pt(P4)} Q${pt(V3)} ${pt(P5)} A${R0} ${R0} 0 0 0 ${pt(P6)} Q${pt(V4)} ${pt(P7)} L${pt(P8)} Q${pt(V1)} ${pt(P1)}Z`;
  };

  const resizeStage = () => {
    const DESIGN_W = 600, DESIGN_H = 700;
    const padX = 8, padY = 16;
    const availW = window.innerWidth - padX * 2;
    const availH = window.innerHeight - padY * 2;
    const scale = Math.min(1, availW / DESIGN_W, availH / DESIGN_H);

    if (containerRef.current) {
      containerRef.current.style.setProperty('--s', scale);
    }
  };

  const handleSpin = async () => {
    if (isSpinning || hasSpun) return;

    setIsSpinning(true);

    try {
      const token = localStorage.getItem('access');
      const sessionKey = localStorage.getItem('wheel_session');

      const headers = {
        'Content-Type': 'application/json',
      };

      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const body = sessionKey ? JSON.stringify({ session_key: sessionKey }) : '{}';

      const response = await fetch(`${API_BASE_URL}/api/miniapp/wheel/spin/`, {
        method: 'POST',
        headers,
        body
      });

      const data = await response.json();

      if (!response.ok) {
        alert(data.error || 'Помилка при прокруті колеса');
        setIsSpinning(false);
        return;
      }

      // Зберігаємо session_key якщо прийшов новий
      if (data.session_key) {
        localStorage.setItem('wheel_session', data.session_key);
      }

      setCurrentSpinResult(data);

      // Знаходимо індекс призу
      const winIndex = prizes.findIndex(p => p.name === data.prize_name);

      spinWheel(winIndex, data.prize_name);

    } catch (error) {
      console.error('Помилка:', error);
      alert('Помилка при прокруті колеса');
      setIsSpinning(false);
    }
  };

  const spinWheel = (winIndex, prizeName) => {
    const N = prizes.length;
    const step = 360 / N;

    const desiredMod = (((360 - winIndex * step - step / 2) % 360) + 360) % 360;
    const currentMod = ((totalRotation % 360) + 360) % 360;
    let delta = desiredMod - currentMod;
    if (delta <= 0) delta += 360;

    const newRotation = totalRotation + 1800 + delta;

    if (wrRef.current) {
      wrRef.current.style.setProperty('--rot', `${newRotation}deg`);
      wrRef.current.classList.add(styles.spinning);
    }

    setTimeout(() => {
      wrRef.current?.classList.remove(styles.spinning);
      if (wrRef.current) {
        wrRef.current.style.transform = `rotate(${newRotation}deg)`;
      }
      setTotalRotation(newRotation);
      animate(prizeName);
    }, 5000);
  };

  const animate = (prize) => {
    // Знаходимо правильний сектор за призом
    // fix: раніше шукали за label.textContent === prize, але тепер назва
    // призу розбита на кілька <tspan> рядків і textContent більше не
    // дорівнює оригінальній назві — тому порівнюємо з окремим
    // data-prize-name, куди повна назва зберігається без змін.
    const allLabels = svgRef.current?.querySelectorAll('text[data-sector]');
    let winLabel = null;
    allLabels?.forEach(label => {
      if (label.getAttribute('data-prize-name') === prize) {
        winLabel = label;
      }
    });

    // Кришка злітає
    if (capRef.current) {
      capRef.current.classList.add(styles.capFlying);
    }

    setTimeout(() => {
      if (dropRef.current) {
        dropRef.current.classList.add(styles.dropFalling);
      }

      // Змивання напису й поява тексту в краплі
      if (winLabel && dropRef.current) {
        syncTextWipe(winLabel, () => {
          const t = document.createElement('div');
          t.className = styles.dropText;
          t.textContent = prize;
          dropRef.current?.appendChild(t);
        });
      }

      setTimeout(() => {
        if (dropRef.current) {
          dropRef.current.style.opacity = '0';
        }

        // Флакон "заряджається" світінням
          bottleRef.current?.classList.add(styles.charging);

        setTimeout(() => {
          bottleRef.current?.classList.remove(styles.charging);

          // Збільшення флакону
          if (bottleRef.current) {
            bottleRef.current.style.transition = 'transform 1.2s cubic-bezier(.32,1.7,.5,1), filter 1.2s ease';
            bottleRef.current.style.transform = 'translate(-50%, -50%) scale(2.8)';
            bottleRef.current.style.filter = 'drop-shadow(0 0 60px rgba(255,220,120,0.95)) brightness(1.2)';
          }

          setTimeout(() => {
            explode();
            if (bottleRef.current) {
              bottleRef.current.style.transition += ', opacity 0.35s ease';
              bottleRef.current.style.opacity = '0';
            }

            // Модалка з'являється поступово: фон темніє одразу,
            // а вікно з призом "конденсується" з диму трохи пізніше
            setModalShow(true);
            requestAnimationFrame(() => setModalDark(true));

            setTimeout(() => {
              setModalMaterialize(true);
            }, 900);

            // Скидання вигляду флакону/краплі/кришки (колесо НЕ скидається)
            setTimeout(() => {
              reset();
              if (winLabel) {
                winLabel.style.opacity = '1';
                winLabel.style.clipPath = '';
                winLabel.style.filter = '';
              }
            }, 3200);
          }, 1200);
        }, 700);
      }, 1900);
    }, 950);
  };

  const syncTextWipe = (label, onFullyWiped) => {
    let wipeRAF = null;

    const frame = () => {
      if (!dropRef.current || !label) return;

      const dropRect = dropRef.current.getBoundingClientRect();
      const labelRect = label.getBoundingClientRect();
      const h = dropRect.height || 80;

      const backEdgeY = dropRect.top + h * 0.04;
      const frontEdgeY = dropRect.top + h * 0.97;
      const labelY = labelRect.top + labelRect.height / 2;

      let raw = (frontEdgeY - labelY) / (frontEdgeY - backEdgeY);
      raw = Math.max(0, Math.min(1, raw));
      const eased = raw * raw * (3 - 2 * raw); // smoothstep

      label.style.clipPath = `inset(${eased * 100}% 0 0 0)`;
      label.style.opacity = `${1 - eased}`;
      label.style.filter = `blur(${eased * 7}px)`;

      if (raw < 1) {
        wipeRAF = requestAnimationFrame(frame);
      } else {
        wipeRAF = null;
        onFullyWiped();
      }
    };

    wipeRAF = requestAnimationFrame(frame);
  };

  const explode = () => {
    const cont = containerRef.current;
    if (!cont) return;

    // Спалах екрану
    const flash = document.createElement('div');
    flash.className = styles.screenFlash;
    document.body.appendChild(flash);
    setTimeout(() => flash.remove(), 600);

    // Тремтіння
    containerRef.current?.classList.add(styles.shake);
    setTimeout(() => containerRef.current?.classList.remove(styles.shake), 450);

    // Ударна хвиля
    const shock = document.createElement('div');
    shock.className = styles.shockwaveRing;
    cont.appendChild(shock);
    setTimeout(() => shock.remove(), 900);

    // Осколки
    for (let i = 0; i < 26; i++) {
      const sh = document.createElement('div');
      sh.style.position = 'absolute';
      sh.style.top = '50%';
      sh.style.left = '50%';
      sh.style.width = `${Math.random() * 30 + 15}px`;
      sh.style.height = `${Math.random() * 30 + 15}px`;
      sh.style.background = `linear-gradient(135deg, rgba(${180 + Math.random() * 45},${140 + Math.random() * 35},${200 + Math.random() * 25},0.9), rgba(${150 + Math.random() * 45},${120 + Math.random() * 35},${180 + Math.random() * 25},0.7))`;
      sh.style.borderRadius = `${Math.random() * 4}px`;
      sh.style.zIndex = '100';
      sh.style.boxShadow = '0 0 10px rgba(255,235,180,0.6)';

      const ang = (i / 26) * Math.PI * 2;
      const dist = 200 + Math.random() * 220;
      sh.style.setProperty('--x', `${Math.cos(ang) * dist}px`);
      sh.style.setProperty('--y', `${Math.sin(ang) * dist}px`);
      sh.style.setProperty('--r', `${Math.random() * 720 - 360}deg`);
      sh.className = styles.explosion;
      sh.style.animationDuration = '1.2s';

      cont.appendChild(sh);
      setTimeout(() => sh.remove(), 1200);
    }

    // Дим
    const puffCount = 14;
    for (let i = 0; i < puffCount; i++) {
      setTimeout(() => {
        const sm = document.createElement('div');
        const size = 150 + Math.random() * 190;
        const startDx = (Math.random() - 0.5) * 160;
        const startDy = (Math.random() - 0.5) * 90 - 10;
        const driftX = (Math.random() - 0.5) * 260;
        const driftUp = 140 + Math.random() * 180;
        const scaleEnd = 2.6 + Math.random() * 2.2;
        const rot = (Math.random() - 0.5) * 70;
        const dur = 2000 + Math.random() * 900;

        const isGold = Math.random() < 0.3;
        const hue = isGold ? 43 : 268;
        const sat = isGold ? 60 : 38;
        const lgt = isGold ? 82 : 84;

        sm.style.position = 'absolute';
        sm.style.top = '50%';
        sm.style.left = '50%';
        sm.style.width = size + 'px';
        sm.style.height = size + 'px';
        sm.style.marginLeft = startDx + 'px';
        sm.style.marginTop = startDy + 'px';
        sm.style.borderRadius = '50%';
        sm.style.background = `radial-gradient(circle at 38% 38%,
          hsla(${hue}, ${sat}%, ${lgt + 8}%, 0.9) 0%,
          hsla(${hue}, ${sat}%, ${lgt}%, 0.75) 30%,
          hsla(${hue}, ${sat - 6}%, ${lgt - 18}%, 0.42) 58%,
          hsla(${hue}, ${sat - 6}%, ${lgt - 18}%, 0) 78%)`;
        sm.style.filter = 'blur(9px)';
        sm.style.zIndex = '999';
        sm.style.pointerEvents = 'none';
        sm.style.setProperty('--dx', driftX + 'px');
        sm.style.setProperty('--dy', (-driftUp) + 'px');
        sm.style.setProperty('--rz', rot + 'deg');
        sm.style.setProperty('--sc', scaleEnd);
        sm.className = styles.smokeRising;
        sm.style.animationDuration = `${dur}ms`;

        cont.appendChild(sm);
        setTimeout(() => sm.remove(), dur + 60);
      }, i * 75);
    }
  };

  const reset = () => {
    if (capRef.current) {
      capRef.current.classList.remove(styles.capFlying);
      capRef.current.style.opacity = '1';
    }
    if (dropRef.current) {
      dropRef.current.classList.remove(styles.dropFalling);
      dropRef.current.style.opacity = '1';
      dropRef.current.innerHTML = `<div class="${styles.dropShape}"></div><div class="${styles.dropHi}"></div><div class="${styles.dropHi2}"></div>`;
    }
    if (bottleRef.current) {
      bottleRef.current.style.transition = '';
      bottleRef.current.style.transform = '';
      bottleRef.current.style.filter = '';
      bottleRef.current.style.opacity = '1';
      bottleRef.current.classList.remove(styles.charging);
    }
  };

  const getViberBotUrl = (context) => {
    const configuredUri = (import.meta.env.VITE_VIBER_CHAT_URI || '').trim();
    const baseUrl = configuredUri.startsWith('viber://pa?')
      ? configuredUri
      : `viber://pa?chatURI=${encodeURIComponent(configuredUri)}`;

    if (!context) return baseUrl;

    const separator = baseUrl.includes('?') ? '&' : '?';
    return `${baseUrl}${separator}context=${encodeURIComponent(context)}`;
  };

  const goToBot = (code) => {
    if (isTelegram) {
      const botUsername = import.meta.env.VITE_TELEGRAM_BOT_USERNAME || 'DLYA_TEBE_perfumes_bot';
      window.location.href = `https://t.me/${botUsername}?start=${code}`;
    } else {
      window.location.href = getViberBotUrl(code);
    }
  };

  // NEW: для програшу коду призу немає — просто відкриваємо бот "з нуля",
  // без ?start= / &context= параметрів, і в телеграмі, і у вайбері.
  const goToBotPlain = () => {
    if (isTelegram) {
      const botUsername = import.meta.env.VITE_TELEGRAM_BOT_USERNAME || 'DLYA_TEBE_perfumes_bot';
      window.location.href = `https://t.me/${botUsername}`;
    } else {
      window.location.href = getViberBotUrl();
    }
  };

  // "1 спін на людину": закриття модалки не скидає можливість крутити
  // повторно — головна кнопка перетворюється на CTA у бот (як і в
  // оригінальній сторінці: closeModal() змінював btn.onclick/текст)
  const closeModal = () => {
    setModalShow(false);
    setModalDark(false);
    setModalMaterialize(false);
    setIsSpinning(false);
    setHasSpun(true);
  };

  // NEW: якщо минулий спін виявився програшним (за флагом lose призу),
  // на екрані "ви вже крутили" показуємо заохочувальний текст замість
  // неіснуючого коду призу.
  const previousIsLose = previousSpin
    ? prizes.find((p) => p.name === previousSpin.prize)?.lose
    : false;

  if (alreadySpun && previousSpin) {
    return (
        <div className={styles.page}>
          <header className={styles.siteHeader}>
            <div className={styles.siteLogo}>Dlya Tebe</div>
        </header>

        <div className={`${styles.alreadyScreen} ${styles.show}`}>
          {previousIsLose ? (
            <>
              <h2>Цього разу не пощастило</h2>
              <p className={styles.aCode}>
                Не засмучуйтесь — у нашому боті регулярно проходять акції з безкоштовними призами. Переходьте, щоб не пропустити наступну!
              </p>
              <button className={styles.btn} onClick={goToBotPlain}>
                Перейти в бот
              </button>
            </>
          ) : (
            <>
              <h2>Ваш подарунок вже чекає на вас</h2>
              <p>Ви отримали:</p>
              <div className={styles.aPrize}>{previousSpin.prize}</div>
              <div className={styles.aCode}>Код: <b>{previousSpin.code}</b></div>
              <button className={styles.btn} onClick={() => goToBot(previousSpin.code)}>
                Перейти в бот за призом
              </button>
            </>
          )}
        </div>
      </div>
    );
  }

  // NEW: чи є поточний результат спіну програшним призом (за флагом lose,
  // що тепер повертається бекендом у списку призів)
  const isLoseResult = currentSpinResult
    ? prizes.find((p) => p.name === currentSpinResult.prize_name)?.lose
    : false;

  return (
    <div className={styles.page}>
      <header className={styles.siteHeader}>
        <div className={styles.siteLogo}>Dlya Tebe</div>
      </header>

      <section className={styles.hero}>
        <h1>Крутіть колесо — отримуйте подарунок</h1>
      </section>

      <section className={styles.wheelSection}>
        <div className={styles.stage} ref={stageRef}>
          <div className={styles.container} ref={containerRef}>
            <div className={styles.wheelWrapper}>
              {/* Фонові плями */}
              <div className={styles.blobs}>
                <div className={styles.blob} style={{ width: '220px', height: '220px', top: '20px', left: '60px', background: '#ff9ec4', filter: 'blur(60px)' }}></div>
                <div className={styles.blob} style={{ width: '200px', height: '200px', top: '0', left: '300px', background: '#ffb27a', filter: 'blur(60px)' }}></div>
                <div className={styles.blob} style={{ width: '220px', height: '220px', top: '230px', left: '400px', background: '#ffd76a', filter: 'blur(60px)' }}></div>
                <div className={styles.blob} style={{ width: '200px', height: '200px', top: '420px', left: '300px', background: '#9de8a8', filter: 'blur(60px)' }}></div>
                <div className={styles.blob} style={{ width: '220px', height: '220px', top: '430px', left: '80px', background: '#7fd6c7', filter: 'blur(60px)' }}></div>
                <div className={styles.blob} style={{ width: '200px', height: '200px', top: '250px', left: '-20px', background: '#8fb8ec', filter: 'blur(60px)' }}></div>
                <div className={styles.blob} style={{ width: '200px', height: '200px', top: '60px', left: '170px', background: '#c79bec', filter: 'blur(60px)' }}></div>
              </div>

              {/* Колесо */}
              <div className={styles.wheelRotate} ref={wrRef}>
                <svg className={styles.wsvg} viewBox="0 0 560 560" ref={svgRef}></svg>
              </div>

              {/* Кільце з лампочками */}
              <div className={styles.outerRing} ref={ringRef}></div>

              {/* Вказівник */}
              <div className={styles.pointer}></div>

              {/* Краплина */}
              <div className={styles.drop} ref={dropRef}>
                <div className={styles.dropShape}></div>
                <div className={styles.dropHi}></div>
                <div className={styles.dropHi2}></div>
              </div>

              {/* Флакон */}
              <div className={styles.bottle} ref={bottleRef}>
                <div className={styles.bCap} ref={capRef}>
                  <div className={styles.bRing}></div>
                </div>
                <div className={styles.bBody}>
                  <div className={styles.bLiquid}></div>
                  <div className={styles.bShine}></div>
                </div>
                <div className={styles.pedestal}></div>
              </div>
            </div>

            {/* fix: кнопка винесена за межі .wheel-wrapper — там живуть лише
                абсолютно позиціоновані декоративні шари колеса (плями,
                колесо, кільце, вказівник, краплина, флакон). Статичний
                (не позиціонований) елемент всередині них завжди
                малюється ПІД ними за правилами stacking context, навіть
                з z-index — тому кнопка й "провалювалась" за колесо. Як
                сусід .wheel-wrapper вона займає власний простір нижче й
                узагалі не перетинається з цими шарами. */}
            <button
              className={styles.btn}
              onClick={
                hasSpun
                  ? () => (isLoseResult ? goToBotPlain() : goToBot(currentSpinResult?.code))
                  : handleSpin
              }
              disabled={isSpinning}
            >
              {isSpinning
                ? 'Крутимо...'
                : hasSpun
                  ? (isLoseResult ? 'Перейти в бот' : 'Забрати приз у боті')
                  : 'Крутити колесо'}
            </button>
          </div>
        </div>
        <p className={styles.trustLine}>Виграш гарантований · 1 спін на людину</p>
      </section>

      {/* Модалка */}
      {modalShow && currentSpinResult && (
          <div className={`${styles.modal} ${styles.show} ${modalDark ? styles.dark : ''}`}>
            <div className={`${styles.mBox} ${modalMaterialize ? styles.materialize : ''}`}>
            {isLoseResult ? (
              <>
                <h2>Цього разу не пощастило 😔</h2>
                <p className={styles.mNote}>
                  Але не сумуйте — у нашому боті регулярно проходять акції з безкоштовними призами. Переходьте в бот прямо зараз, щоб не пропустити наступну нагоду виграти!
                </p>
                <button onClick={() => { closeModal(); goToBotPlain(); }}>Перейти в бот</button>
              </>
            ) : (
              <>
                <h2>Вітаємо! 🎉</h2>
                <p>Ви виграли:</p>
                <div className={styles.mPrize}>{currentSpinResult.prize_name}</div>
                <p className={styles.mNote}>Натисніть кнопку нижче — у чаті бота одразу з'явиться все необхідне для отримання вашого призу.</p>
                <button onClick={() => { closeModal(); goToBot(currentSpinResult.code); }}>Забрати приз у боті</button>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default BonusWheel;