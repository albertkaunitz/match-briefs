# -*- coding: utf-8 -*-
# Справка комментатора: «Красный Яр» · ВВА-Подмосковье, 12 тур ЧР по регби, 29.08.2026.
# Дизайн-код эталона (Электрон/ЦСКА) 1:1: style и классы взяты как есть, изменены только данные.
# Отличие от футбольных сборок: слой «Протокол» опирается на регбийную нумерацию 1..23 (номер = позиция).
import os, re, base64, datetime

# Момент сборки проставляется машиной, а не руками: штамп актуальности в шапке
# и подпись в подвале обязаны говорить правду после каждой пересборки.
СОБРАНО = datetime.datetime.now()
СОБРАНО_ТЕКСТ = СОБРАНО.strftime("%d.%m.%Y, %H:%M")
СОБРАНО_ISO = СОБРАНО.strftime("%Y-%m-%dT%H:%M:%S+03:00")

ENGINE = "/Users/Rapido/Desktop/12 НЕДЕЛЬ/Комментаторство/5_Инструменты-песочница/_Методика-справки/_движок"
STYLE   = open(os.path.join(ENGINE,"etalon_style.css"), encoding="utf-8").read().strip()
SCRIPTS = open(os.path.join(ENGINE,"etalon_scripts.js"), encoding="utf-8").read().strip()
# Сторож свежести в эталоне настроен на прошлый матч (сбор 24.07, 17-й тур футбольной лиги).
# Без перенастройки регбийный бриф показывал бы чужое предупреждение.
_watch_old = re.search(r"var СБОР='[^']*', ТУРЫ=\[.*?\]\];", SCRIPTS, re.S)
if not _watch_old:
    raise SystemExit("сторож свежести не найден в etalon_scripts.js: проверить движок")
SCRIPTS = SCRIPTS.replace(_watch_old.group(0),
    "var СБОР='2026-08-26', ТУРЫ=[['2026-08-29','12-й тур, этот матч'],['2026-09-06','13-й тур']];")
SCRIPTS = SCRIPTS.replace("(после 16 туров)", "(после 11 туров)")

# ---------- Пульт эфира ----------
# Комментатор отмечает произнесённое прямо в брифе: галочка на плашке, счётчик остатка,
# режим «скрыть сказанное». Отметки живут в браузере (localStorage) и переживают
# перезагрузку страницы, включая ту, что делает сверщик версий при выходе новой сборки.
# Ключ хранилища привязан к адресу матча: отметки одного брифа не протекают в другой,
# хотя все брифы лежат на одном домене.
CHECKLIST_JS = r"""
// Штамп актуальности живёт сам: показывает момент сбора данных и их возраст,
// пересчитывая его раз в минуту. Пишем ровно то, что правда: когда данные сняты
// с официальных источников. Само содержимое обновляет пересборка брифа.
(function(){
  var поле = document.getElementById('freshness');
  if (!поле) return;
  var собрано = new Date(поле.getAttribute('data-built'));
  if (isNaN(собрано)) return;
  var текст = поле.querySelector('.freshness__text');

  function два(ч){ return (ч < 10 ? '0' : '') + ч; }

  function обновить(){
    var минут = Math.floor((Date.now() - собрано.getTime()) / 60000);
    var часов = минут / 60;
    var дата = два(собрано.getDate()) + '.' + два(собрано.getMonth() + 1) + '.' + собрано.getFullYear();
    var время = два(собрано.getHours()) + ':' + два(собрано.getMinutes());
    var возраст;
    if (минут < 2)        возраст = 'только что';
    else if (минут < 60)  возраст = минут + ' мин назад';
    else if (часов < 24)  возраст = Math.floor(часов) + ' ч назад';
    else {
      var дней = Math.floor(часов / 24);
      var хвост = (дней % 10 === 1 && дней % 100 !== 11) ? 'день'
                : ((дней % 10 >= 2 && дней % 10 <= 4 && (дней % 100 < 10 || дней % 100 >= 20)) ? 'дня' : 'дней');
      возраст = дней + ' ' + хвост + ' назад';
    }
    поле.classList.toggle('freshness--stale', часов >= 12 && часов < 48);
    поле.classList.toggle('freshness--old', часов >= 48);
    текст.textContent = 'Актуально на ' + дата + ', ' + время;
    поле.title = 'Данные сняты с официальных источников ' + возраст;
  }

  обновить();
  setInterval(обновить, 60000);
})();

(function(){
  // Один и тот же бриф открывается и как «…/матч/», и как «…/матч/index.html».
  // Без нормализации это два разных ключа, и отметки эфира «теряются» при переходе.
  var КЛЮЧ = 'brief-said:' + location.pathname.replace(/index\.html?$/i, '');
  var сказано = new Set();
  try { сказано = new Set(JSON.parse(localStorage.getItem(КЛЮЧ) || '[]')); } catch(e) {}

  function сохранить(){
    try { localStorage.setItem(КЛЮЧ, JSON.stringify(Array.from(сказано))); } catch(e) {}
  }

  var плашки = Array.prototype.slice.call(document.querySelectorAll('details.acc--say'));
  if (!плашки.length) return;

  function пересчитать(){
    var всего = плашки.length, отмечено = 0;
    плашки.forEach(function(d){ if (d.classList.contains('acc--said')) отмечено++; });
    var поле = document.getElementById('sayCount');
    if (поле) {
      поле.innerHTML = отмечено >= всего
        ? 'Проговорено всё: <b>' + всего + '</b>'
        : 'Осталось сказать <b>' + (всего - отмечено) + '</b> из ' + всего;
    }
  }

  плашки.forEach(function(d){
    var имя = d.getAttribute('data-say') || '';
    var кнопка = document.createElement('span');
    кнопка.className = 'say-btn';
    кнопка.setAttribute('role', 'button');
    кнопка.setAttribute('aria-label', 'отметить как сказанное');
    кнопка.title = 'Сказал в эфире';
    кнопка.textContent = '✓';
    d.querySelector('summary').appendChild(кнопка);

    if (сказано.has(имя)) d.classList.add('acc--said');

    кнопка.addEventListener('click', function(ев){
      ев.preventDefault();      // клик по галочке не должен раскрывать плашку
      ев.stopPropagation();
      var стало = d.classList.toggle('acc--said');
      if (стало) { сказано.add(имя); d.open = false; } else { сказано.delete(имя); }
      сохранить();
      пересчитать();
    });
  });

  var скрывать = document.getElementById('hideSaid');
  if (скрывать) скрывать.addEventListener('click', function(){
    var включено = document.body.classList.toggle('hide-said');
    скрывать.classList.toggle('toolbar__btn--on', включено);
    скрывать.textContent = включено ? 'Показать сказанное' : 'Скрыть сказанное';
  });

  var сброс = document.getElementById('resetSaid');
  if (сброс) сброс.addEventListener('click', function(){
    сказано.clear(); сохранить();
    плашки.forEach(function(d){ d.classList.remove('acc--said'); });
    document.body.classList.remove('hide-said');
    if (скрывать) { скрывать.classList.remove('toolbar__btn--on'); скрывать.textContent = 'Скрыть сказанное'; }
    пересчитать();
  });

  пересчитать();
})();
"""
SCRIPTS = SCRIPTS + "\n" + CHECKLIST_JS
def b64(p): return base64.b64encode(open(os.path.join(ENGINE,"logos",p),"rb").read()).decode()
KY_L  = "data:image/png;base64,"+b64("ky.png")
VVA_L = "data:image/png;base64,"+b64("vva.png")
CHR_L = "data:image/png;base64,"+b64("chr-emblem.png")   # эмблема «Чемпионата России», rugby.ru
HERO  = "data:image/jpeg;base64,"+b64("hero_bg.jpg")     # команда «Красного Яра» на своём стадионе, yarrugby.ru

# ---------- дизайн-код: коллаборация двух клубов ----------
# Палитра собрана из фирменных стилей обеих команд, снятых с их официальных сайтов:
#   «Красный Яр»  — изумруд навигации yarrugby.ru #009D7A и глубокий зелёный клубной
#                   афиши этого матча (#004C34, доминанта YAr_VVA.jpg);
#   ВВА-Подмосковье — тёмно-синий шапки vva-podmoskovie.ru #00167F и красный #E63A2E.
# Смысл раскладки: слева всегда хозяева и зелёный, справа всегда гости и синий.
# База нейтральная тёмная с лёгким зелёным подтоном: долго смотреть в эфире не устанешь.
# Профиль: ~/.claude/identity/clients/rugby-ky-vva.json
PALETTE = """
:root{
  --bg:#101614;--bg-card:#17211D;--bg-divider:#1C2A25;--bg-row:#141D1A;--bg-row-2:#16201C;
  --accent:#00B383;--accent-soft:rgba(0,179,131,0.12);--accent-dim:rgba(0,179,131,0.30);
  --text:#fff;--text-muted:#9DB3AA;--text-dim:#71877E;
  --border:#25342E;--border-soft:#1E2A25;
  --result-w:#00B383;--result-l:#E63A2E;--result-d:#71877E;--warn:#e6b800;
  /* стороны матча */
  --home:#00C08B;--home-deep:#004C34;--home-soft:rgba(0,192,139,0.10);
  --away:#5B8CFF;--away-deep:#00167F;--away-soft:rgba(91,140,255,0.10);--away-red:#E63A2E;
}

/* Шапка: слева цвет хозяев, справа цвет гостей. */
.site-header{background:linear-gradient(90deg,var(--home-deep) 0%,var(--bg-card) 45%,var(--bg-card) 55%,var(--away-deep) 100%);border-bottom:1px solid var(--border);}

/* Карточка матча: фотография стадиона хозяев, поверх зелёное свечение слева и синее справа. */
.match-card{position:relative;overflow:hidden;background:var(--bg-card);}
.match-card::before{content:"";position:absolute;inset:0;background-image:url("ФОТО");background-size:cover;background-position:center 40%;opacity:.42;}
.match-card::after{content:"";position:absolute;inset:0;background:
   linear-gradient(90deg,rgba(0,76,52,0.62) 0%,rgba(16,22,20,0.80) 40%,rgba(16,22,20,0.80) 60%,rgba(0,22,127,0.62) 100%);}
.match-card>*{position:relative;z-index:1;}
.match-card__team:first-child .match-card__team-city{color:var(--home);}
.match-card__team:last-child .match-card__team-city{color:var(--away);}

/* Вкладки команд окрашены своей стороной. */
.tab[data-tab="ky"].tab--active{color:var(--home);border-bottom-color:var(--home);}
.tab[data-tab="vva"].tab--active{color:var(--away);border-bottom-color:var(--away);}

/* Турнирная таблица: строки наших команд помечены полосой своей стороны. */
.standings-mini__row--home{box-shadow:inset 3px 0 0 var(--home);background:var(--home-soft);}
.standings-mini__row--away{box-shadow:inset 3px 0 0 var(--away);background:var(--away-soft);}
.standings-mini__row--home .team,.standings-mini__row--home .pts{color:var(--home);}
.standings-mini__row--away .team,.standings-mini__row--away .pts{color:var(--away);}

/* Протокол: номер и амплуа хозяев зелёные, гостей синие. */
.pr-side--home .pr-num{color:var(--home);}
.pr-side--away .pr-num{color:var(--away);}
.pr-row{background:linear-gradient(90deg,var(--home-soft) 0%,transparent 22%,transparent 78%,var(--away-soft) 100%);}
.pr-head{border-top:2px solid transparent;border-image:linear-gradient(90deg,var(--home) 0%,var(--bg-divider) 50%,var(--away) 100%) 1;}

/* Штамп актуальности: в самой верхней плашке справа, на стороне гостей.
   Возраст данных пересчитывает сама страница раз в минуту, поэтому «свежо» не протухает незаметно. */
/* Полоса растёт под содержимое: в эталоне у неё была жёсткая высота 54px, и на телефоне
   заголовок из трёх строк вылезал наружу, а штамп ложился поверх текста. */
.site-header{display:flex;align-items:center;flex-wrap:wrap;gap:0 12px;row-gap:9px;
  height:auto;min-height:54px;padding:12px 16px 11px;}
.site-header img{order:0;flex:0 0 100%;width:100%;height:34px;object-fit:contain;display:block;}
/* В эталоне заголовок стоял absolute по центру полосы: он не занимал места,
   поэтому полоса не росла под три строки, а текст накрывал штамп. Возвращаем в поток. */
.site-header__title{position:static;left:auto;transform:none;
  order:1;flex:1 1 auto;text-align:center;padding:0 6px;line-height:1.25;}
/* Номер тура идёт своей строкой: разделитель-точка при переносе повисал в конце строки. */
.site-header__tour{display:block;}
/* Распорка справа больше не нужна: эмблема стоит своей строкой по центру,
   заголовок центрируется сам по всей ширине полосы. */
/* Штамп актуальности идёт отдельной строкой под названием тура, внутри той же полосы. */
.site-header .freshness{order:3;flex:1 1 100%;justify-content:center;}
.freshness{display:inline-flex;align-items:center;gap:7px;font-size:10.5px;line-height:1.3;
  color:rgba(255,255,255,0.82);background:rgba(0,0,0,0.28);border:1px solid rgba(255,255,255,0.18);
  border-radius:20px;padding:5px 11px;white-space:nowrap;flex:0 0 auto;}
.freshness__dot{width:7px;height:7px;border-radius:50%;background:var(--home);flex:0 0 auto;
  box-shadow:0 0 0 3px rgba(0,192,139,0.18);}
.freshness--stale .freshness__dot{background:var(--warn);box-shadow:0 0 0 3px rgba(230,184,0,0.18);}
.freshness--old .freshness__dot{background:var(--away-red);box-shadow:0 0 0 3px rgba(230,58,46,0.18);}
@media (max-width:560px){
  .site-header{padding:11px 12px 10px;}
  .site-header .freshness{font-size:10px;padding:4px 10px;}
}

/* Адрес арены по центру карточки матча, части адреса не рвутся посреди слова. */
.match-card__location{text-align:center;line-height:1.5;}

/* Подвал: источники сверху, бренд ниже, контакт последним. Ничего не рвётся посреди слова. */
.site-footer__copyright{line-height:1.6;}
.site-footer__brand{white-space:nowrap;}
.site-footer__sources{display:block;}
.site-footer__sources-note{display:block;}
.site-footer__line{display:block;margin-top:9px;}
.site-footer__contact{display:block;margin-top:10px;}
.site-footer__contact a{display:inline-flex;align-items:center;gap:6px;color:var(--home);
  text-decoration:none;border-bottom:1px solid var(--home);padding-bottom:1px;white-space:nowrap;font-weight:600;}
.site-footer__contact a:hover{color:var(--text);border-bottom-color:var(--text);}

/* Шапка на телефоне: номер тура и формат эфира переносятся целиком, а не рвутся пополам. */
.nowrap{white-space:nowrap;display:inline-block;}
@media (max-width:520px){
  .tour-header__meta{flex-direction:column;align-items:flex-start;gap:5px;}
  .tour-header__meta-item{white-space:nowrap;}
}

/* ===== Пульт эфира: отметка «сказано» на каждой реплике ===== */
.acc--say>summary{align-items:center;}
.say-btn{width:30px;height:30px;min-width:30px;border-radius:50%;border:1.5px solid var(--border);
  display:inline-flex;align-items:center;justify-content:center;margin-left:10px;flex:0 0 auto;
  cursor:pointer;color:var(--text-dim);font-size:15px;line-height:1;background:var(--bg-row);
  transition:background .15s,border-color .15s,color .15s;-webkit-tap-highlight-color:transparent;}
.say-btn:hover{border-color:var(--accent);color:var(--accent);}
.acc--said>summary .say-btn{background:var(--accent);border-color:var(--accent);color:#04140E;font-weight:800;}
.acc--said>summary .acc__title{opacity:.42;text-decoration:line-through;}
.acc--said>summary .acc__hint{opacity:.32;}
.acc--said{border-color:var(--border-soft);}
body.hide-said .acc--said{display:none;}
.panel[data-panel="ky"] .acc--said>summary .say-btn{background:var(--home);border-color:var(--home);}
.panel[data-panel="vva"] .acc--said>summary .say-btn{background:var(--away);border-color:var(--away);color:#050B22;}
.say-count{margin-left:auto;font-size:11px;font-weight:700;letter-spacing:0.04em;color:var(--text-muted);
  display:inline-flex;align-items:center;gap:6px;white-space:nowrap;}
.say-count b{color:var(--accent);font-size:13px;}
.toolbar{flex-wrap:wrap;align-items:center;}
.toolbar__btn--on{border-color:var(--accent);color:var(--accent);}
@media (max-width:520px){.say-count{width:100%;margin:6px 0 0;}}

/* Блоки команд: заголовок раздела красится стороной. */
.panel[data-panel="ky"] .section-divider{box-shadow:inset 3px 0 0 var(--home);}
.panel[data-panel="vva"] .section-divider{box-shadow:inset 3px 0 0 var(--away);}
.panel[data-panel="ky"] .on-air{background:linear-gradient(135deg,rgba(0,192,139,0.10),rgba(0,192,139,0.02));border-left-color:var(--home);}
.panel[data-panel="vva"] .on-air{background:linear-gradient(135deg,rgba(91,140,255,0.10),rgba(91,140,255,0.02));border-left-color:var(--away);}
.panel[data-panel="ky"] .fact__num{background:var(--home);color:#04140E;}
.panel[data-panel="vva"] .fact__num{background:var(--away);color:#050B22;}
.panel[data-panel="ky"] .kv__label{color:var(--home);}
.panel[data-panel="vva"] .kv__label{color:var(--away);}
"""

# Переменных мало: часть цветов футбольной лиги вшита в дизайн-код литералами
# (градиенты карточки матча, подложки логотипов, оттенки текста). Их тоже
# переводим в палитру мероприятия, иначе на странице местами светится салатовый.
ПЕРЕКРАСКА = {
  "#18191b":"#101614", "#232527":"#17211D", "#2a2c2f":"#1C2A25", "#1f2123":"#141D1A",
  "#212325":"#16201C", "#1a1c1e":"#141D1A", "#2f3134":"#25342E", "#252729":"#1E2A25",
  "#A4D639":"#00B383", "#a4d639":"#00B383", "164,214,57":"0,179,131",
  "#8a8f95":"#9DB3AA", "#5e6166":"#71877E", "#6b6f74":"#71877E",
  "#d64541":"#E63A2E", "#e3e5e7":"#E2EDE8", "#d6d8da":"#D3E0DA", "#c9ccd0":"#C4D5CD",
  "#8d2b0f":"#4A2A12", "#f5c451":"#F2C14E", "#ffd97a":"#F7D9A0", "#8a6d1f":"#7A5A2A",
  "#3d2b0f":"#2E2410", "#cdd0d4":"#CDDCD5", "#ff6b6b":"#E63A2E", "#62c7d9":"#5B8CFF",
  "#2fa84f":"#00B383", "47,168,79":"0,179,131",   # зелёный «победа» из эталона: уводим в цвет хозяев
}
for _старый, _новый in ПЕРЕКРАСКА.items():
    STYLE = STYLE.replace(_старый, _новый)
PALETTE = PALETTE.replace("ФОТО", HERO)

RUGBY = "https://rugby.ru/seasons/chempionat-rossii-2026/"
YAR   = "http://yarrugby.ru/news/"
VVAS  = "https://vva-podmoskovie.ru/news/"

# ---------- конструкторы блоков эталона ----------
def angle(label, fact_, quote, src, href, hint=""):
    # acc--say: единица, которую комментатор произносит в эфире. Такие плашки получают
    # галочку «сказано» и попадают в счётчик. Ключ отметки строится из data-say,
    # то есть из заголовка: он переживает пересборку брифа, в отличие от порядкового номера.
    return f'''<details class="acc acc--say" data-say="{label}"><summary><span class="acc__title">{label}</span><span class="acc__hint">{hint}</span></summary><div class="acc__body">
      <div class="angle-fact">{fact_}</div>
      <p class="angle-quote">{quote}</p>
      <span class="bundle__source"><a href="{href}" target="_blank" rel="noopener">{src}&nbsp;↗</a></span>
      </div></details>'''

def st_row(pos, team, i, w, d, l, gz, gp, rio, bo, o, cls=""):
    return f'''<div class="standings-mini__row{cls}"><span class="pos">{pos}</span><span class="team">{team}</span><span>{i}</span><span>{w}</span><span>{d}</span><span>{l}</span><span>{gz} : {gp}</span><span>{rio}</span><span>{bo}</span><span class="pts">{o}</span></div>'''

def mrow(date, tour, venue, home, score, away, res):
    return f'''<div class="match-row">
      <div class="match-row__when"><span class="match-row__date">{date}</span><span class="match-row__tour">{tour}</span><span class="match-row__venue">{venue}</span></div>
      <div class="match-row__teams"><span class="match-row__side match-row__side--home"><span class="match-row__name">{home}</span></span><span class="match-row__score">{score}</span><span class="match-row__side match-row__side--away"><span class="match-row__name">{away}</span></span></div>
      <span class="match-row__result match-row__result--{res}"><span>{res}</span></span>
    </div>'''

def fact(num, label, data, phrase, src, href, hint=""):
    return f'''<details class="acc acc--say" data-say="{label}"><summary><span class="acc__title"><span class="fact__num">{num}</span>{label}</span><span class="acc__hint">{hint}</span></summary><div class="acc__body">
      <div class="fact__data">{data}</div>
      <div class="fact__phrase">{phrase}</div>
      <div class="fact__source"><a href="{href}" target="_blank" rel="noopener">{src}&nbsp;↗</a></div>
      </div></details>'''

def players(rows, note=""):
    """Ключевые игроки как плашки пульта: у каждого своя галочка «сказал в эфире».
    Вход тот же, что был у kv(): пары («№1 · столб, капитан», «<b>Имя</b>, остальное»).
    Имя вытаскивается из <b> и уходит в заголовок, чтобы игрока было видно списком,
    а позиция остаётся подсказкой справа. Ключ отметки строится из имени: он переживает
    правку текста карточки, в отличие от ключа по всей строке."""
    куски = []
    for label, text in rows:
        m = re.search(r'<b>(.*?)</b>', text)
        имя = m.group(1) if m else label
        номер = label.split('·')[0].strip()
        роль = label.split('·', 1)[1].strip() if '·' in label else ''
        тело = text[m.end():].lstrip(', ') if m else text
        куски.append(
            f'<details class="acc acc--say acc--player" data-say="игрок: {имя}">'
            f'<summary><span class="acc__title">{номер} · {имя}</span>'
            f'<span class="acc__hint">{роль}</span></summary>'
            f'<div class="acc__body"><div class="player__text">{тело}</div></div></details>')
    tail = f'<div class="kv__note">{note}</div>' if note else ""
    return "".join(куски) + tail

def kv(rows, note=""):
    body = "".join(f'<div class="kv__row"><span class="kv__label">{a}</span><span class="kv__val">{b}</span></div>' for a, b in rows)
    tail = f'<div class="kv__note">{note}</div>' if note else ""
    return f'<div class="kv">{body}{tail}</div>'

def prow(hn, hp, hname, an, ap, aname):
    return f'''<div class="pr-row"><span class="pr-side pr-side--home"><span class="pr-num">{hn}</span><span class="pr-role">{hp}</span><span class="pr-name">{hname}</span></span><span class="pr-side pr-side--away"><span class="pr-name">{aname}</span><span class="pr-role">{ap}</span><span class="pr-num">{an}</span></span></div>'''

def grp(title, rows):
    """Группа протокола. Класса pr-group в дизайн-коде эталона нет (движок его объявлял, стиль не завезли),
    поэтому группа собирается на существующих классах: кликабельный section-divider плюс pr-list."""
    return f'<div class="section-divider">{title}</div><div class="pr-list" style="border-radius:0">{"".join(rows)}</div>'

# ---------- СЛОЙ 1: превью, углы подачи ----------
angles = "".join([
 angle("Перед стартом: минута молчания",
       "25 августа на 48-м году жизни скоропостижно скончался один из лучших российских арбитров Алексей Алексеевич Брызгалин. Федерация регби России приняла решение начать все соревнования, проходящие с 28 по 31 августа, с минуты молчания в его память. Прощание состоится 31 августа в Москве.",
       "Перед началом сегодняшнего матча мы хотим вспомнить человека, который огромную часть своей жизни посвятил российскому регби.</p><p class='angle-quote'>25 августа скоропостижно ушёл из жизни Алексей Алексеевич Брызгалин, один из ведущих российских арбитров, лучший судья России 2021 года.</p><p class='angle-quote'>В регби он пришёл ещё ребёнком. Был игроком, детским тренером, руководителем спортивной школы, а с 2006 года посвятил себя судейству. Работал на крупнейших российских турнирах и международных матчах, в том числе на Кубке мира по регби-7 в Москве.</p><p class='angle-quote'>Для нескольких поколений российских регбистов Алексей Брызгалин был неотъемлемой частью этой игры: человеком, чьи профессионализм, принципиальность и преданность регби оставили заметный след в истории.</p><p class='angle-quote'>Сегодня российское регби прощается с одним из легендарных его представителей.</p><p class='angle-quote'>Светлая память легенде российского регби Алексею Алексеевичу Брызгалину.</p><p class='angle-quote'>Объявляется минута молчания.",
       "сайт Федерации регби России, 28.08", "https://rugby.ru/news/minuta-molchaniya-v-pamyat-ob-aleksee-bryzgaline/", "сказать до первого свистка"),
 angle("Цена матча: путёвка в плей-офф",
       "Клуб объявил ставку прямым текстом за пять дней до игры: «Один матч, одна победа и „Красный Яр“ обеспечит себе место в плей-офф».",
       "«Красноярцы выходят на матч, в котором победа решает не тур, а сезон: она закрывает вопрос с плей-офф».",
       "яrugby.ru, новость 24.08", YAR, "победа = плей-офф"),
 angle("Тренер назвал цифру: десять баллов",
       "Ульрих Бейерс перед этими двумя турами: «нам нужны десять турнирных баллов в следующих матчах со „Славой-МАР“ и „ВВА-Подмосковьем“». Пять баллов из десяти уже взяты 23 августа, победа со Славой прошла с бонусом атаки.",
       "«Половину задачи Бейерс закрыл неделю назад. Сегодня он приехал за второй половиной, и это значит: побеждать мало, нужен бонус».",
       "интервью Бейерса, 21.08", "http://yarrugby.ru/news/ulrikh-beyers-my-mozhem-pobedit-lyubuyu-komandu-v-chempionate-rossii.htm", "нужен бонус атаки"),
 angle("Что такое бонус атаки в этом матче",
       "В регби очки в таблицу даёт не только победа. Команда получает дополнительный балл за четыре и более занесённые попытки. У «Красного Яра» пять таких бонусов за сезон, у ВВА за десять матчей ни одного.",
       "«Следите не только за счётом. Четвёртая попытка хозяев это отдельное событие: она приносит очко в таблицу».",
       "таблица ЧР, колонка «Бонус»", RUGBY, "5 бонусов против 0"),
 angle("Первый круг: единственный намёк на сопротивление",
       "15 мая в Монино ВВА уступила 32:40. Это лучший матч подмосковных против «Яра» за сезон и один из немногих, где они набрали больше тридцати очков.",
       "«В мае в Монино эта пара выдала пятизначную перестрелку на семьдесят два очка. Если ВВА повторит тот матч, вечер получится не проходным».",
       "календарь ЧР-2026", RUGBY, "ВВА 32:40 КЯ"),
 angle("Разрыв, который трудно вообразить",
       "Разница очков: у «Красного Яра» плюс 35, у ВВА минус 268. За три последних тура подмосковные пропустили 172 очка при 34 забитых.",
       "«Минус двести шестьдесят восемь. Такой разницы нет ни у кого в лиге, и она набрана не в один вечер».",
       "таблица ЧР-2026", RUGBY, "+35 против −268"),
 angle("Обидная серия хозяев: три поражения в концовках",
       "До победы над «Славой» у «Яра» шли поражения от топ-3 с минимальным счётом: 24:25 от «Динамо», 29:30 от «Енисея-СТМ», 13:17 от «Стрелы-Ак Барс».",
       "«Красноярцы весь второй круг проигрывают лучшим по очку. Тренер говорит, что должны были выигрывать все три».",
       "интервью Бейерса, 21.08", "http://yarrugby.ru/news/ulrikh-beyers-my-mozhem-pobedit-lyubuyu-komandu-v-chempionate-rossii.htm", "24:25, 29:30, 13:17"),
 angle("Схватка перестала быть слабым местом",
       "Бейерс: «Сейчас наши молы и схватки серьёзное оружие. Тренер нападающих Руан Смит добился огромных успехов в этом направлении». Речь о линии, которая годами была проблемой клуба.",
       "«Смотрите на схватку и мол: то, за что „Яр“ годами получал упрёки, тренер теперь называет оружием».",
       "интервью Бейерса, 21.08", "http://yarrugby.ru/news/ulrikh-beyers-my-mozhem-pobedit-lyubuyu-komandu-v-chempionate-rossii.htm", "молы и схватки"),
 angle("Ротация: новый капитан и десять новых лиц",
       "Тренер обещал ротацию «в разумных пределах» и провёл её второй матч подряд. В старте на эту игру десять новых игроков против состава со «Славой», повязка перешла от восьмого номера Аллена Де Вита к столбу Валерию Морозову, самого Де Вита в заявке нет. Неделю назад ротация сработала: Чабан занёс попытку, Елисеев первую за основу, Семёнов реализовал.",
       "«Бейерс снова переписал состав: десять новых игроков и капитан из первой линии. Ставка та же, что неделю назад, и неделю назад она сыграла».",
       "составы клуба 22.08 и 28.08", "http://yarrugby.ru/news/", "10 новых, капитан Морозов"),
 angle("У гостей всё держится на девятом номере",
       "Александр Казаков это капитан ВВА, скрам-хав и штатный бьющий. В матче со «Стрелой» он набрал все двенадцать очков первого тайма четырьмя штрафными, в матче со «Славой» реализовал решающую попытку.",
       "«Если у ВВА будет шанс набрать очки, почти наверняка их наберёт девятый номер: Казаков и капитан, и бьющий».",
       "отчёты клуба ВВА", VVAS, "Казаков: капитан и бьющий"),
 angle("Два бывших титана друг напротив друга",
       "У «Красного Яра» 12 чемпионств СССР и России, у ВВА-Подмосковья 9 титулов СССР и 8 российских. Сейчас это четвёртая и шестая команды лиги из семи.",
       "«Матч двух клубов, у которых на двоих под тридцать чемпионских титулов. Сегодня они делят четвёртое и шестое места из семи».",
       "истории клубов на сайте ФРР", "https://rugby.ru/teams/krasnyj-yar/", "12 титулов против 17"),
 angle("Лифт из школы работает",
       "19 августа СШОР «Красный Яр» выиграла Первенство России U18, обыграв в финале «Приморец-ОН» из Санкт-Петербурга 27:20.",
       "«За неделю до этого матча школа „Яра“ стала лучшей в стране среди восемнадцатилетних. Это тот резерв, который через год окажется на этом поле».",
       "яrugby.ru, новость 19.08", YAR, "U18 чемпион России"),
 angle("Трое красноярцев в заявке гостей",
       "В составе ВВА на этот матч трое родившихся в Красноярске. Столб Александр Новик, 23 года, вырос в школе «Енисея-СТМ». Фуллбэк Виталий Безматерных, 22 года, тоже воспитанник школы «Енисея», играл за этот клуб до 2026 года и перешёл в ВВА этим летом. Запасной Дмитрий Пастернак, 28 лет, мастер спорта, родился здесь же. Новик и Безматерных выходят в стартовом составе.",
       "«Гости привезли в Красноярск троих своих. Новик и Безматерных выросли в школе „Енисея-СТМ“, Безматерных ещё в прошлом сезоне играл за „Енисей“, а сегодня выходит против клуба, с которым его команда спорит всю жизнь. Третий, Дмитрий Пастернак, ждёт на скамейке».",
       "vva-podmoskovie.ru, страницы игроков", "https://vva-podmoskovie.ru/team/mans/players-m.html", "трое своих в гостях"),
 angle("Восемь чемпионств гостей выиграны при одном тренере",
       "Николай Владимирович Неруш, 66 лет, заслуженный тренер России, числится тренером мужской команды ВВА. Главным тренером клуба он был с 1990 по 2018 год и ещё раз в 2021: под его руководством ВВА восемь раз выигрывала чемпионат России и восемь раз Кубок России. С 1993 по 2005 год он же возглавлял сборную России по регби-7 и вывел её на Кубок мира, а сборную по регби-15 привёл на Кубок мира 2011 года. В протокол этого матча он не внесён: на игру заявлены врио главного тренера Андрей Сорокин и второй тренер Александр Хрокин, так что на скамейке его сегодня может не быть.",
       "«У этого клуба восемь чемпионств и восемь Кубков России, и все они выиграны при одном тренере. Николай Неруш вёл ВВА двадцать восемь лет и он же вывел сборную России на её первый Кубок мира. Сегодня команду ведёт врио главного тренера Андрей Сорокин, а сама она идёт шестой из семи с разницей минус двести шестьдесят восемь».",
       "vva-podmoskovie.ru, тренерский штаб", "https://vva-podmoskovie.ru/team/vva-administration.html", "8 чемпионств и 8 Кубков"),
])

# ---------- Турнирная таблица ----------
standings = "".join([
 st_row("1","Динамо",10,9,0,1,388,159,"+229",5,41),
 st_row("2","Стрела-Ак Барс",9,7,1,1,253,155,"+98",4,34),
 st_row("3","Енисей-СТМ",9,6,1,2,335,168,"+167",7,33),
 st_row("4","Красный Яр",9,4,0,5,259,224,"+35",5,21," standings-mini__row--home"),
 st_row("5","Локомотив",10,3,0,7,206,304,"−98",4,16),
 st_row("6","ВВА-Подмосковье",10,2,0,8,160,428,"−268",0,8," standings-mini__row--away"),
 st_row("7","Слава МАР",9,1,0,8,115,278,"−163",3,7),
])

# Места проведения берутся только оттуда, где их назвал официальный источник:
# анонсы и отчёты клубов на yarrugby.ru и vva-podmoskovie.ru, страница клуба Енисей-СТМ.
МОНИНО   = "Монино · стадион «ВВА-Подмосковье», Новинское шоссе, стр. 9"
КРАСНОЯР = "Красноярск · стадион «Красный Яр», ул. Маерчака, 57"
АВАНГАРД = "Красноярск · стадион «Авангард»"
ПЕНЗА    = "Пенза · стадион «Первомайский», ул. Калинина, 119"
КАЗАНЬ   = "Казань · стадион «Тулпар»"
СЛАВА    = "Москва · стадион «Слава», ул. Селезнёвская, 13Ас1"

h2h = "".join([
 mrow("15.05.2026","3 тур",МОНИНО,"ВВА-Подмосковье","32 : 40","Красный Яр","В"),
])

ky_form = "".join([
 mrow("12.06","6 тур",ПЕНЗА,"Локомотив","19 : 57","Красный Яр","В"),
 mrow("28.06","7 тур",КРАСНОЯР,"Красный Яр","24 : 25","Динамо","П"),
 mrow("09.08","9 тур",КРАСНОЯР,"Красный Яр","13 : 17","Стрела-Ак Барс","П"),
 mrow("16.08","10 тур",АВАНГАРД,"Енисей-СТМ","30 : 29","Красный Яр","П"),
 mrow("23.08","11 тур",КРАСНОЯР,"Красный Яр","45 : 10","Слава МАР","В"),
])

vva_form = "".join([
 mrow("13.06","6 тур",КАЗАНЬ,"Стрела-Ак Барс","45 : 26","ВВА-Подмосковье","П"),
 mrow("04.07","8 тур",МОНИНО,"ВВА-Подмосковье","15 : 14","Слава МАР","В"),
 mrow("08.08","9 тур",СЛАВА,"Динамо","68 : 7","ВВА-Подмосковье","П"),
 mrow("15.08","10 тур",ПЕНЗА,"Локомотив","55 : 22","ВВА-Подмосковье","П"),
 mrow("22.08","11 тур",МОНИНО,"ВВА-Подмосковье","5 : 49","Енисей-СТМ","П"),
])

# Почему в форме «Красного Яра» нет 5-го и 8-го туров: в лиге семь команд,
# в каждом туре играют три пары, одна команда отдыхает. Прочтение календаря ФРР.
ПРОПУСК_КЯ = kv([
 ("Почему нет 5-го и 8-го туров","В Чемпионате России по регби семь команд. В туре проходят три матча, и одна команда каждый раз остаётся без игры. По календарю Федерации «Красный Яр» отдыхал в 5-м туре (6 и 8 июня) и в 8-м (4 и 5 июля): матчей у команды в эти даты нет. Отсюда и разница в сыгранных матчах, у «Яра» их девять, у ВВА и «Локомотива» по десять."),
 ("Что это значит для таблицы","У «Красного Яра» на матч меньше, чем у ближайшего преследователя, и запас по очкам он добирает как раз в таких турах."),
], "Прочтение календаря сезона на rugby.ru: перечень матчей каждого тура. Отдельного объявления Федерации о переносе нет, потому что переноса и не было.")

# ---------- СЛОЙ 3: по пять фактов на команду ----------
ky_facts = "".join([
 fact("01","Семь попыток в последнем матче",
      "23 августа «Красный Яр» обыграл «Славу-МАР» 45:10, занеся семь попыток против одной. Первый тайм 28:10.",
      "Соперник тот же класс, что и сегодняшний: последний раз хозяева отгрузили аутсайдеру семь попыток.",
      "отчёт клуба, 23.08", "http://yarrugby.ru/news/krasnyy-yar-obygral-slavu-mar-s-bonusom-ataki%20%2023.htm", "45:10 со «Славой»"),
 fact("02","Таумалоло: четыре реализации подряд",
      "В матче со «Славой» флай-хав Джейсон Таумалоло реализовал четыре попытки: на 4-й, 21-й, 32-й и 35-й минутах.",
      "Десятый номер хозяев отвечает за очки после попыток. Его нога в этом матче будет работать часто.",
      "отчёт клуба, 23.08", "http://yarrugby.ru/news/krasnyy-yar-obygral-slavu-mar-s-bonusom-ataki%20%2023.htm", "10-й номер, бьющий"),
 fact("03","Капитана прошлого матча в заявке нет",
      "Неделю назад команду выводил восьмой номер Аллен Де Вит: попытка на 3-й минуте и жёлтая карточка на 37-й. В заявке на эту игру его нет вовсе, повязку получил столб Валерий Морозов.",
      "Капитан, который открыл счёт в прошлом туре и там же схлопотал десять минут, сегодня остался вне заявки.",
      "составы клуба 22.08 и 28.08", "http://yarrugby.ru/news/", "повязка сменилась"),
 fact("04","Ротация в чистом виде: десять новых игроков в старте",
      "Между матчем со «Славой» и этим стартовый состав сменился на две трети. Из пятнадцати вышедших 23 августа на поле снова выходят пятеро: Мамрикишвили, Лосенков, Архип, Таумалоло, Абдулкадиров. Капитанскую повязку у Аллена Де Вита забрал столб Валерий Морозов, самого Де Вита в заявке на этот матч нет.",
      "Тренер обещал ротацию в разумных пределах и сделал её по-крупному: десять новых игроков в старте и новый капитан.",
      "составы клуба на 22.08 и 28.08", "http://yarrugby.ru/news/", "10 новых из 15"),
 fact("05","Клуб с 1969 года и 12 титулов",
      "Основан в 1969 году: секцию в Красноярском политехническом институте создал Леонид Тихонович Сабинин, команда называлась «Политехник». Двукратный чемпион СССР, десятикратный чемпион России, десятикратный обладатель Кубка.",
      "Красноярск это регбийная столица страны по числу титулов, и «Яр» её главная вывеска.",
      "профиль клуба на сайте ФРР", "https://rugby.ru/teams/krasnyj-yar/", "1969, «Политехник»"),
])

vva_facts = "".join([
 fact("01","Ноль бонусных очков за сезон",
      "После десяти туров у ВВА в колонке «Бонус» стоит ноль. Это единственная команда лиги без бонусных очков.",
      "Ни разу за сезон подмосковные не занесли четыре попытки в одном матче и ни разу не проиграли в пределах семи очков.",
      "таблица ЧР-2026", RUGBY, "единственные в лиге"),
 fact("02","Пять очков за весь прошлый матч",
      "22 августа дома ВВА уступила «Енисею-СТМ» 5:49. Одна попытка без реализации за восемьдесят минут.",
      "Неделю назад в Монино они набрали пять очков. Сегодня им нужно занести хотя бы столько же в Красноярске.",
      "таблица и календарь ЧР", RUGBY, "5:49 от «Енисея»"),
 fact("03","Казаков решает всё",
      "Капитан Александр Казаков бьёт штрафные и реализации. В матче со «Стрелой» он принёс все 12 очков первого тайма, в победном матче со «Славой» реализовал попытку Джураева.",
      "Девятый номер гостей это их атака, их очки и их капитан в одном лице.",
      "отчёты клуба ВВА", VVAS, "12 очков за тайм"),
 fact("04","Единственная победа с июля",
      "4 июля дома ВВА обыграла «Славу-МАР» 15:14. Крылаткин забил дроп-гол, Джураев и Шмелёв занесли попытки, оборона выстояла в концовке.",
      "Последний раз подмосковные побеждали почти два месяца назад, и то одним очком.",
      "отчёт клуба ВВА", VVAS, "15:14 со «Славой»"),
 fact("05","Команда военных лётчиков с 1967 года",
      "Создана в 1967 году в Монино при Военно-воздушной академии имени Гагарина. Инициатор: начальник академии, маршал авиации, Герой Советского Союза Красовский. Девятикратный чемпион СССР, восьмикратный чемпион России.",
      "Их зовут военлётами не для красоты: клуб вырос из Военно-воздушной академии.",
      "профиль клуба на сайте ФРР", "https://rugby.ru/teams/vva-podmoskove/", "«военлёты», Монино"),
])

# ---------- СЛОЙ 4: протокол по регбийным номерам ----------
POS = {
 1:"столб", 2:"хукер", 3:"столб", 4:"замок", 5:"замок", 6:"фланкер", 7:"фланкер", 8:"восьмой",
 9:"скрам-хав", 10:"флай-хав", 11:"крыло", 12:"центр", 13:"центр", 14:"крыло", 15:"фуллбэк",
}
# Состав «Красного Яра» на ЭТОТ матч, опубликован клубом 28.08.2026.
KY_XV = {1:"Валерий Морозов (к)",2:"Бека Мамрикишвили",3:"Евгений Пронин",4:"Данил Лосенков",5:"Александр Худяков",
 6:"Йохан Ретиф",7:"Владимир Арлашов",8:"Виктор Архип",9:"Хушнуд Сангинов",10:"Джейсон Таумалоло",
 11:"Буркуталы Тойчуев",12:"Лоуренс Преториус",13:"Андрей Шакура",14:"Ислам Абдулкадиров",15:"Дилан Смит"}
# Состав ВВА-Подмосковья на ЭТОТ матч, опубликован клубом в телеграм-канале 29.08.2026 в 10:03.
VVA_XV = {1:"Александр Новик",2:"Грант Товмасян",3:"Кирилл Собачкин",4:"Никита Арлашов",5:"Никита Акулинчев",
 6:"Александр Шахов",7:"Владислав Фризен",8:"Михаил Жлутков",9:"Александр Казаков (к)",10:"Егор Кулешов",
 11:"Дмитрий Дрождин",12:"Сергей Мотов",13:"Станислав Шмелев",14:"Джурабек Джураев",15:"Виталий Безматерных"}
KY_BENCH = {16:"Дмитрий Кузеро",17:"Михеил Ратиашвили",18:"Иван Селиванов",19:"Анеле Лунгиса",
 20:"Александр Елисеев",21:"Данил Попов",22:"Даниил Семёнов",23:"Павел Фиц"}
VVA_BENCH = {16:"Александр Иванов",17:"Иван Нежданов",18:"Данил Зяблицев",19:"Ярослав Гаманов",
 20:"Кирилл Панарин",21:"Максим Агафонов",22:"Сергей Тришин",23:"Дмитрий Пастернак"}

pack   = [prow(n, POS[n], KY_XV[n], n, POS[n], VVA_XV[n]) for n in range(1,9)]
halves = [prow(n, POS[n], KY_XV[n], n, POS[n], VVA_XV[n]) for n in range(9,11)]
backs  = [prow(n, POS[n], KY_XV[n], n, POS[n], VVA_XV[n]) for n in range(11,16)]
# Состав гостей сверен с официальным протоколом матча Федерации регби России (файл заявки,
# получен 29.08). Протокол разошёлся с телеграм-анонсом клуба на девятнадцатом номере:
# в анонсе стоял Капустянский, в протоколе Гаманов. Держим протокол.
# Амплуа запасных по официальным страницам игроков: yarrugby.ru/team и vva-podmoskovie.ru.
# Агафонов заявлен из дубля, его карточка на странице молодёжной команды клуба.
KY_BENCH_POS = {16:"хукер",17:"столб",18:"столб",19:"замок",20:"замок",
 21:"скрам-хав",22:"флай-хав",23:"центр"}
VVA_BENCH_POS = {16:"нападающий",17:"столб",18:"столб",19:"замок",20:"фланкер",
 21:"скрам-хав",22:"центр",23:"третья линия"}
bench  = [prow(n, KY_BENCH_POS[n], KY_BENCH[n], n, VVA_BENCH_POS[n], VVA_BENCH[n]) for n in range(16,24)]

STAFF_MAIN = "".join([
 '<div class="pr-row pr-row--staff"><span class="pr-side pr-side--home"><span class="pr-role">главный тренер</span><span class="pr-name pr-name--accent">Ульрих Бейерс</span></span><span class="pr-side pr-side--away"><span class="pr-name pr-name--accent">Андрей Сорокин</span><span class="pr-role">врио главного тренера</span></span></div>',
 '<div class="pr-row pr-row--staff"><span class="pr-side pr-side--home"><span class="pr-role">тренер нападающих</span><span class="pr-name">Руан Смит</span></span><span class="pr-side pr-side--away"><span class="pr-name">Александр Хрокин</span><span class="pr-role">второй тренер</span></span></div>',
])
STAFF_REST = "".join([
 '<div class="pr-row"><span class="pr-side pr-side--home"><span class="pr-role">форма</span><span class="pr-name">зелёно-чёрная, по клубной афише матча</span></span><span class="pr-side pr-side--away"><span class="pr-name">красная майка, чёрные трусы, красные гетры</span><span class="pr-role">форма</span></span></div><div class="pr-row"><span class="pr-side pr-side--home"><span class="pr-role">клуб</span><span class="pr-name">АНО «Спортивный регбийный клуб „Красный Яр“», Красноярск</span></span><span class="pr-side pr-side--away"><span class="pr-name">РК «ВВА-Подмосковье», Монино, Новинское шоссе, стр. 9</span><span class="pr-role">клуб</span></span></div>',
 '<div class="pr-row"><span class="pr-side pr-side--home"><span class="pr-role">штаб</span><span class="pr-name">Ульрих Бейерс, Руан Смит</span></span><span class="pr-side pr-side--away"><span class="pr-name">Кушнарев К. (менеджер), Косарев (массажист), Горошилов и Агафонов (водоносы)</span><span class="pr-role">в протоколе</span></span></div>',
])

судьи = kv([
 ("Судья в поле","<b>Алексей Куликов</b>, Москва"),
 ("Первый помощник","Максим Крамской, Москва"),
 ("Второй помощник","Умар Хомидов, Красноярск"),
 ("Резервный судья","Александр Егоров, Красноярск"),
 ("Судья видеоповторов","Артур Каптюх, Москва"),
 ("Комиссар матча","Сергей Мурашкин, Красноярск"),
], "Назначения опубликованы в анонсе матча на сайте Федерации регби России, 28 августа.")

# Изменения в составах, объявленные Федерацией в анонсе матча.
ИЗМЕНЕНИЯ = kv([
 ("«Красный Яр»","С первых минут выходит <b>Валерий Морозов</b>, Михеил Ратиашвили остаётся в запасе. Место основного девятого номера занимает <b>Хушнуд Сангинов</b>. Вне заявки на матч: Руди Ван Ройен, Аллен Стефан де Вит, Дмитрий Сухин и Мхлели Дламини."),
 ("ВВА-Подмосковье","Точечные изменения, три позиции из пятнадцати. В стартовом составе выходят <b>Джурабек Джураев</b> на четырнадцатом номере и <b>Виталий Безматерных</b> фуллбэком, <b>Даниил Крылаткин</b> матч пропускает. <b>Дмитрий Пастернак</b> с одиннадцатого номера ушёл в запас, крыло занял <b>Дмитрий Дрождин</b>. Капитан прежний, скрам-хав <b>Александр Казаков</b>. Тринадцать из пятнадцати играли неделю назад с «Енисеем-СТМ»: у гостей ротации почти нет, в отличие от хозяев. На скамейке официальный протокол разошёлся с анонсом клуба: под девятнадцатым номером заявлен замок <b>Ярослав Гаманов</b>, а не Владислав Капустянский. Гаманов ростом 203 см, самый высокий человек в этом матче."),
], "Источник: анонс матча на сайте Федерации регби России, 28 августа. Номера позиций Федерация не называет, поэтому по номерам эти замены не расставлены.")

# ---------- Вкладка «Регби в эфире» ----------
score_rules = kv([
 ("Попытка, 5 очков","Мяч приземлён в зачётной зоне соперника. Главное событие матча и единственный способ получить бонусное очко: четыре попытки за игру дают команде дополнительный балл в таблицу."),
 ("Реализация, 2 очка","Удар по воротам с подставки сразу после попытки. Мяч должен пройти между стоек и над перекладиной. Бьют с точки напротив места приземления, поэтому попытка под штангами дороже попытки у флажка."),
 ("Штрафной удар, 3 очка","Назначается за нарушение. Команда может выбрать удар по воротам, и тогда это три очка, либо разыграть, отправив мяч в аут и получив коридор у зачётной зоны."),
 ("Дроп-гол, 3 очка","Удар по воротам с игры: мяч сначала опускают на землю, затем бьют с отскока. Редкий и эффектный способ, в этом сезоне у ВВА его исполнял Даниил Крылаткин, но на этот матч он не заявлен."),
], "Формулировки по разделу «Основные правила регби» на сайте Федерации регби России.")

nums_rules = kv([
 ("Номер это позиция","В регби номер на спине жёстко привязан к роли. Увидел номер, знаешь, кто перед тобой и что он должен делать. Это работает для обеих команд одинаково."),
 ("1, 2, 3 первая линия","Столб, хукер, столб. Держат схватку. Тяжелейшая физическая работа матча, именно про эту линию тренер «Яра» говорит, что она перестала быть слабым местом."),
 ("4 и 5 вторая линия","Замки. Самые высокие в команде, выигрывают мяч в коридоре, толкают в схватке и в моле."),
 ("6, 7, 8 третья линия","Фланкеры и восьмой. Первые в захватах и в борьбе за мяч на земле. Восьмой номер часто капитан и таранная сила."),
 ("9 и 10 полузащита","Скрам-хав выдаёт мяч из схватки, флай-хав принимает решения и обычно бьёт по воротам. Это два мозговых центра команды."),
 ("11, 12, 13, 14 линия трёх четвертей","Центры и крылья. Через них идёт скорость и заносятся попытки на флангах."),
 ("15 фуллбэк","Последний защитник и первый контратакующий, ловит дальние удары."),
], "Роли даны по разделу «Правила регби и функции игроков» на сайте Федерации регби России.")

air_rules = kv([
 ("Что говорить, когда счёт стоит","В регби между очками проходят долгие отрезки борьбы за территорию. Это время для контекста: цена матча, плей-офф, судьба серии, история клубов."),
 ("Считать бонусы вслух","В этом матче отдельная драма это четвёртая попытка хозяев. Проговаривайте счётчик попыток, зрителю не очевидно, что победа бывает дороже победы."),
 ("22 метра и штрафной","Заход в зону 22 метров и заработанный штрафной это план хозяев, который тренер описал словами. Называйте это планом, а не случайностью."),
 ("Мол и схватка","Мол это движение группой с мячом в руках, схватка это фиксированное построение восьми на восемь. Для «Яра» и то и другое названо тренером оружием."),
 ("Жёлтая карточка","Десять минут вне поля. В регби это почти всегда пропущенная попытка, потому что команда играет вчетырнадцатером."),
], "")

flash = kv([
 ("Если «Яр» выигрывает крупно","Спросить у тренера, удалось ли сохранить силы перед плей-офф и кто из ротации заслужил место в основе на полуфинал."),
 ("Если «Яр» выигрывает без бонуса","Тема разговора: десять баллов, о которых говорил Бейерс, взяты не полностью. Что не получилось в атаке."),
 ("Если ВВА держится","Спросить, что изменил Сорокин после 5:49 от «Енисея» и на чём держалась оборона."),
 ("Если играет молодёжь ВВА","У клуба своя молодёжная команда в Лиге молодёжных команд, многие фамилии из неё дублируются в основе. Вопрос про переход из дубля в основу."),
 ("Общий вопрос обоим","Полуфинал с «Динамо» реален для «Яра». Вопрос: что нужно изменить, чтобы не проигрывать лидерам по одному очку."),
], "")

BODY = f'''
<div class="wrap">
  <div class="site-header">
    <img src="{CHR_L}" alt="Чемпионат России по регби" style="height:34px;width:auto">
    <div class="site-header__title"><span class="nowrap">Чемпионат России по регби 2026</span><span class="site-header__tour">12 тур</span></div>
    <div class="freshness" id="freshness" data-built="{СОБРАНО_ISO}">
      <span class="freshness__dot"></span>
      <span class="freshness__text">Актуально на {СОБРАНО_ТЕКСТ}</span>
    </div>
  </div>

  <div class="stale" id="staleWarn"></div>

  <div class="tour-header">
    <div class="tour-header__meta">
      <span class="tour-header__meta-item">Регулярный чемпионат · до плей-офф два тура</span>
      <span class="tour-header__meta-item">Онлайн-эфир</span>
    </div>
  </div>

  <div class="match-card">
    <div class="match-card__location">📍 <span class="nowrap">Стадион «Красный Яр»</span> · <span class="nowrap">ул. Маерчака, 57</span> · <span class="nowrap">Красноярск</span></div>
    <div class="match-card__main">
      <div class="match-card__team"><img src="{KY_L}" alt="Красный Яр"><div class="match-card__team-name">Красный Яр</div><div class="match-card__team-city">4-е место · 21 очко</div></div>
      <div class="match-card__center"><div class="match-card__date">29 августа</div><div class="match-card__weekday">суббота</div><div class="match-card__time">13:00 мск</div></div>
      <div class="match-card__team"><img src="{VVA_L}" alt="ВВА-Подмосковье"><div class="match-card__team-name">ВВА-Подмосковье</div><div class="match-card__team-city">6-е место · 8 очков</div></div>
    </div>
    <div class="match-card__footer"><strong>Формат</strong> онлайн-эфир · 17:00 по местному времени, Красноярск это Москва плюс четыре часа · <a href="https://video.sports.ru/stream/ncPRxPfU2fo56Yep-VGMXiWO438aKoDVIYyw0lix_H4" target="_blank" rel="noopener">трансляция матча&nbsp;↗</a></div>
  </div>

  <div class="tabs">
    <button class="tab tab--active" data-tab="preview">Превью</button>
    <button class="tab" data-tab="ky">Красный Яр</button>
    <button class="tab" data-tab="vva">ВВА</button>
    <button class="tab" data-tab="protocol">Протокол</button>
    <button class="tab" data-tab="rugby">Регби в эфире</button>
  </div>

  <div class="toolbar">
    <button class="toolbar__btn" id="expandAll">Развернуть всё</button>
    <button class="toolbar__btn" id="collapseAll">Свернуть всё</button>
    <button class="toolbar__btn" id="hideSaid">Скрыть сказанное</button>
    <button class="toolbar__btn" id="resetSaid">Сбросить</button>
    <span class="say-count" id="sayCount"></span>
  </div>

  <!-- ПРЕВЬЮ -->
  <div class="panel panel--active" data-panel="preview">
    <div class="section-divider">Турнирная окрестность</div>
    <div style="padding:14px 16px">
      <div class="standings-mini">
        <div class="standings-mini__head"><span>#</span><span>Команда</span><span>И</span><span>В</span><span>Н</span><span>П</span><span>Очки за</span><span>РИО</span><span>Б</span><span>О</span></div>
        {standings}
        <div class="standings-mini__note">После 11 туров · источник rugby.ru, официальный сайт Федерации регби России</div>
      </div>
    </div>
    <div class="section-divider">Очная встреча этого сезона</div>
    <div style="padding:14px 16px"><div class="matches-list">{h2h}</div></div>
    <div class="section-divider">Углы подачи матча</div>
    <div style="padding:14px 16px">{angles}</div>
  </div>

  <!-- КРАСНЫЙ ЯР -->
  <div class="panel" data-panel="ky">
    <div class="section-divider">Красный Яр · 4-е место, 21 очко</div>
    <div style="padding:14px 16px">
      <div class="on-air"><div class="on-air__label">Кто это</div><p>Самый титулованный клуб страны в сложном сезоне: четвёртое место, три поражения от лидеров с разницей в одно очко и одна победа до плей-офф. Тренер Ульрих Бейерс говорит, что команда близка к лучшим и что схватка стала оружием.</p></div>
      <details class="acc" open><summary><span class="acc__title">Форма · последние 5 матчей</span><span class="acc__hint">В-П-П-П-В</span></summary><div class="acc__body"><div class="matches-list">{ky_form}</div></div></details>
      <details class="acc" open><summary><span class="acc__title">Ключевые игроки</span><span class="acc__hint">каждого отмечаем отдельно</span></summary><div class="acc__body">{players([
        ("№1 · столб, капитан на этот матч","<b>Валерий Морозов</b>, 31 год, 190 см, 121 кг, мастер спорта. Родом из Киргизии. Единственный в лиге с таким послужным списком в Англии: играл за «Сейл Шаркс», «Бат» и «Вустер», до того «Зеленоград», «Енисей-СТМ» и ЦСКА. В «Красном Яре» с 2023 года. Сегодня выводит команду с повязкой."),
        ("№10 · флай-хав","<b>Джейсон Таумалоло</b>, 24 года, 184 см, 94 кг. Из Тонги, играл за «Майрост», в «Красном Яре» с 2020 года. Бьющий: в матче со «Славой» реализовал четыре попытки подряд. Через него идут все очки после приземлений."),
        ("№8 · восьмой","<b>Виктор Архип</b>, 36 лет, 192 см, 112 кг, мастер спорта. Из Молдавии, прошёл её клубы и «Енисей-СТМ», в «Красном Яре» с 2014 года. Самый возрастной в старте и главный таран третьей линии."),
        ("№9 · скрам-хав","<b>Хушнуд Сангинов</b>, 26 лет, 172 см, 75 кг, кандидат в мастера спорта. Воспитанник красноярской школы «Красный Яр», играет и девятым, и пятнадцатым номером. Свой, местный."),
        ("№5 · замок","<b>Александр Худяков</b>, 36 лет, 190 см, 109 кг, мастер спорта. Воспитанник «Красного Яра», в команде с 2010 года: шестнадцатый сезон в одном клубе."),
        ("№12 · центр","<b>Лоуренс Преториус</b>, 31 год, 186 см, 100 кг. Из ЮАР, в клубе с 2022 года. Занёс последнюю попытку матча со «Славой», на 80-й минуте."),
        ("№15 · фуллбэк","<b>Дилан Смит</b>, 25 лет, 188 см, 86 кг. Из ЮАР, пришёл из «Грифонс». Последний защитник и первый контратакующий."),
      ], "Паспорта игроков: официальный сайт клуба, раздел «Мужская команда». Возраст посчитан на день матча.")}</div></details>
      <details class="acc"><summary><span class="acc__title">Куда делись 5-й и 8-й туры</span><span class="acc__hint">в лиге семь команд</span></summary><div class="acc__body">{ПРОПУСК_КЯ}</div></details>
      {ky_facts}
    </div>
  </div>

  <!-- ВВА -->
  <div class="panel" data-panel="vva">
    <div class="section-divider">ВВА-Подмосковье · 6-е место, 8 очков</div>
    <div style="padding:14px 16px">
      <div class="on-air"><div class="on-air__label">Кто это</div><p>Военлёты из Монино, девятикратные чемпионы СССР, сегодня шестые из семи. Две победы за сезон, ноль бонусных очков и минус 268 по разнице. Командой с 2024 года руководит врио главного тренера Андрей Сорокин.</p></div>
      <details class="acc" open><summary><span class="acc__title">Форма · последние 5 матчей</span><span class="acc__hint">П-В-П-П-П</span></summary><div class="acc__body"><div class="matches-list">{vva_form}</div></div></details>
      <details class="acc" open><summary><span class="acc__title">Ключевые игроки</span><span class="acc__hint">каждого отмечаем отдельно</span></summary><div class="acc__body">{players([
        ("№9 · скрам-хав, капитан","<b>Александр Казаков</b>, 23 года, 177 см, 72 кг, мастер спорта. Из Ногинска, воспитанник подмосковной школы, первый тренер Фукс. В «ВВА-Подмосковье» с 2019 года, золото Кубка России по регби-7 2021. Капитан и штатный бьющий: со «Стрелой» принёс все 12 очков первого тайма четырьмя штрафными. Почти все очки команды идут через него."),
        ("№1 · столб","<b>Александр Новик</b>, 23 года, 179 см, 110 кг, мастер спорта. Родился в Красноярске и вырос в школе «Енисея-СТМ»: сегодня он играет в родном городе против клуба, с которым его школа соперничает всю жизнь. Четырежды чемпион России среди молодёжи. В заявке он такой не один: фуллбэк Виталий Безматерных тоже красноярец из школы «Енисея-СТМ», а запасной Дмитрий Пастернак родился в Красноярске. Трое своих в гостях у чужого клуба."),
        ("№15 · фуллбэк","<b>Виталий Безматерных</b>, 22 года, 182 см, 90 кг, мастер спорта. Красноярец: родился в этом городе, воспитанник школы «Енисея-СТМ», первый тренер Сергей Крыкса. До 2026 года играл за «Енисей-СТМ», в ВВА пришёл этим летом. Сегодня выходит в родном Красноярске против клуба, с которым «Енисей» соперничает всю жизнь. Четырежды чемпион страны среди молодёжи, серебро чемпионата Европы по регби-7 U18. По амплуа центр веера, сегодня поставлен последним защитником."),
        ("№10 · флай-хав","<b>Егор Кулешов</b>, 28 лет, 186 см, 93 кг, мастер спорта. Из Ногинска, в регби с 2005 года, выступал за сборную России по регби-7. Второй распасовщик после Казакова."),
        ("№8 · восьмой","<b>Михаил Жлутков</b>, 25 лет, 190 см, 84 кг, кандидат в мастера спорта. Москвич, воспитанник школы в Долгопрудном, играет за сборную Московской области. В основе весь сезон без пропусков."),
      ], "Паспорта игроков: официальный сайт клуба, карточки раздела «Мужская команда». Возраст посчитан на день матча.")}</div></details>
      {vva_facts}
    </div>
  </div>

  <!-- ПРОТОКОЛ -->
  <div class="panel" data-panel="protocol">
    <div class="protocol-section-title">Протокол: кто под каким номером</div>
    <div class="pr-head">
      <div class="pr-head__side" style="flex-direction:row;align-items:center;gap:8px"><img src="{KY_L}" alt="Красный Яр" style="width:30px;height:30px;object-fit:contain"><div><div class="pr-head__name">Красный Яр</div><div class="pr-head__city">4-е место</div></div></div>
      <div class="pr-head__center">составы на матч</div>
      <div class="pr-head__side pr-head__side--away" style="flex-direction:row;align-items:center;gap:8px;justify-content:flex-end"><div style="text-align:right"><div class="pr-head__name">ВВА-Подмосковье</div><div class="pr-head__city">6-е место</div></div><img src="{VVA_L}" alt="ВВА" style="width:30px;height:30px;object-fit:contain"></div>
    </div>
    <div style="padding:10px 16px 0"><div class="standings-mini__note" style="border:none;padding:0 0 8px">Оба состава <b>на этот матч</b> и сверены с официальными протоколами: «Красный Яр» по анонсу клуба, ВВА-Подмосковье по протоколу Федерации. Что меняется против прошлого тура, вынесено в блок ниже. Номер в регби это позиция, поэтому пара строк читается как противостояние на одном месте поля.</div></div>
    <div style="padding:0 16px 6px">
      <details class="acc" open><summary><span class="acc__title">Изменения в составах на этот матч</span><span class="acc__hint">по анонсу Федерации</span></summary><div class="acc__body">{ИЗМЕНЕНИЯ}</div></details>
    </div>
    {grp("Схватка · номера с 1 по 8", pack)}
    {grp("Полузащита · номера 9 и 10", halves)}
    {grp("Линия трёх четвертей · номера с 11 по 15", backs)}
    {grp("Запасные · номера с 16 по 23", bench)}
    <div class="protocol-section-title" style="margin-top:14px">Тренерский штаб</div>
    <div class="pr-head">
      <div class="pr-head__side" style="flex-direction:row;align-items:center;gap:8px"><img src="{KY_L}" alt="Красный Яр" style="width:26px;height:26px;object-fit:contain"><div class="pr-head__name">Красный Яр</div></div>
      <div class="pr-head__center">тренеры</div>
      <div class="pr-head__side pr-head__side--away" style="flex-direction:row;align-items:center;gap:8px;justify-content:flex-end"><div class="pr-head__name">ВВА-Подмосковье</div><img src="{VVA_L}" alt="ВВА" style="width:26px;height:26px;object-fit:contain"></div>
    </div>
    <div class="pr-list">{STAFF_MAIN}</div>
    <div style="padding:10px 16px 0">
      <details class="acc"><summary><span class="acc__title">Клубы и остальной штаб</span><span class="acc__hint">по сайтам клубов</span></summary><div class="acc__body" style="padding:0"><div class="pr-list" style="border:none">{STAFF_REST}</div></div></details>
    </div>
    <div style="padding:14px 16px">
      <div class="protocol-section-title" style="margin-top:14px">Судейская бригада</div>
      <div style="padding:10px 16px 0">{судьи}</div>
      <ul class="checklist-live">
        <li class="check--done"><span class="check-badge check-badge--done">✓</span><span class="check-text">Состав «Красного Яра» на матч<span class="check-source">опубликован клубом 28 августа, внесён в протокол выше</span></span></li>
        <li class="check--done"><span class="check-badge check-badge--done">✓</span><span class="check-text">Судейская бригада<span class="check-source">анонс матча на сайте Федерации, 28 августа</span></span></li>
        <li class="check--done"><span class="check-badge check-badge--done">✓</span><span class="check-text">Трансляция: <a href="https://video.sports.ru/stream/ncPRxPfU2fo56Yep-VGMXiWO438aKoDVIYyw0lix_H4" target="_blank" rel="noopener">video.sports.ru, прямой эфир матча&nbsp;↗</a><span class="check-source">ссылку дал клуб в анонсе состава</span></span></li>
        <li class="check--done"><span class="check-badge check-badge--done">✓</span><span class="check-text">Полный состав ВВА-Подмосковья<span class="check-source">сверен с официальным протоколом матча Федерации; девятнадцатый номер по протоколу Гаманов, а не Капустянский из клубного анонса</span></span></li>
      </ul>
    </div>
  </div>

  <!-- РЕГБИ В ЭФИРЕ -->
  <div class="panel" data-panel="rugby">
    <div class="section-divider">Как считаются очки</div>
    <div style="padding:14px 16px">{score_rules}</div>
    <div class="section-divider">Номер это позиция</div>
    <div style="padding:14px 16px">{nums_rules}</div>
    <div class="section-divider">Эфирные акценты этого матча</div>
    <div style="padding:14px 16px">{air_rules}</div>
    <div class="section-divider">Флеш-интервью: развилки</div>
    <div style="padding:14px 16px">{flash}</div>
  </div>

  <div class="site-footer">
    <div class="site-footer__copyright" style="text-align:center">
      <span class="site-footer__sources">Источники: <span class="nowrap">rugby.ru</span> · <span class="nowrap">yarrugby.ru</span> · <span class="nowrap">vva-podmoskovie.ru</span></span>
      <span class="site-footer__sources-note">все официальные</span>
      <span class="site-footer__line">Справка комментатора · разработана по методике <span class="site-footer__brand">MKD AI Boutique</span></span>
      <span class="site-footer__contact"><a href="https://t.me/albertkaunitz" target="_blank" rel="noopener">@albertkaunitz</a></span>
    </div>
    <div class="site-footer__private" style="text-align:center">Оба состава на этот матч, судейская бригада, штаб и ссылка на трансляцию внесены и сверены с официальными протоколами Федерации регби России.</div>
  </div>
</div>

<script>
{SCRIPTS}
</script>
'''

HTML = f'''<!-- identity: clients/rugby-ky-vva.json -->
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Справка комментатора · Красный Яр · ВВА-Подмосковье · ЧР по регби, 12 тур · 29.08.2026</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
{STYLE}
{PALETTE}
/* Место проведения пишется полностью: город, стадион, улица. В эталоне это поле
   было коротким («дома» / «в гостях») и обрезалось по ширине в одну строку. */
.match-row__venue{{max-width:none;white-space:normal;overflow:visible;text-overflow:clip;line-height:1.35;}}
.match-row__when{{min-width:210px;}}
@media (max-width:520px){{.match-row__when{{min-width:0;}}}}
/* Карточка игрока — вложенная плашка пульта внутри «Ключевых игроков».
   Отступ слева отделяет её от родителя, текст читается абзацем. */
.acc--player{{margin:0 0 6px;}}
.acc--player .acc__title{{font-weight:700;}}
.player__text{{color:var(--text);line-height:1.5;font-size:13px;}}
/* Плашка роли в эталоне стояла с flex-shrink:0 и фиксированной строкой: длинная роль
   («28 лет главным тренером») распирала свою половину и наезжала на имя соседней команды.
   Разрешаем плашке сжиматься и переносить текст, имя при этом не обрезается. */
.pr-role{{flex-shrink:1;min-width:0;white-space:normal;line-height:1.25;}}
.pr-row--staff .pr-name{{overflow:visible;text-overflow:clip;}}
/* Эмблема турнира приходит чёрной графикой: на тёмной подложке выводим её белой. */
.site-header img{{filter:brightness(0) invert(1);opacity:.92;}}
/* Регбийная таблица шире футбольной на две колонки: РИО и бонусные очки.
   Дизайн-код эталона не меняется, правится только сетка строки под 10 колонок. */
.standings-mini__head,.standings-mini__row{{grid-template-columns:22px minmax(0,1fr) 26px 24px 24px 24px 80px 46px 26px 30px;}}
.standings-mini__head>span,.standings-mini__row>span{{white-space:nowrap;}}
.standings-mini__row .team{{overflow:hidden;text-overflow:ellipsis;}}
@media (max-width:520px){{.standings-mini__head,.standings-mini__row{{font-size:10px;grid-template-columns:16px minmax(0,1fr) 18px 16px 16px 16px 66px 38px 18px 22px;padding:7px 6px;}}
.standings-mini__head>span,.standings-mini__row>span{{padding-left:4px;}}}}
</style>
</head>
<body>
{BODY}
</body>
</html>'''

# ---- Гейты перед записью ----
def gate(html):
    errors = []
    text = re.sub(r"<[^>]+>", " ", re.sub(r"<style>.*?</style>|<script>.*?</script>", " ", html, flags=re.S))
    dashes = [d for d in re.findall(r"[^>]{0,40}—[^<]{0,40}", text) if len(d.strip()) > 3]
    if dashes:
        errors.append(f"длинных тире в тексте: {len(dashes)}. Первое: …{dashes[0].strip()[:70]}…")
    for m in re.finditer(r'<ul class="staff-list">(.*?)</ul>', html, re.S):
        if len(re.sub(r"<[^>]+>", "", m.group(1))) > 200:
            errors.append("проза в staff-list: нужен kv()")
    if "expandAll" not in html:
        errors.append("нет интерактива: кнопки «развернуть/свернуть всё»")
    # Пульт эфира: плашки-реплики, кнопка отметки и хранилище отметок должны доехать до страницы.
    сказать = html.count('acc--say"') + html.count('acc--say ')
    if сказать < 10:
        errors.append(f"пульт эфира: плашек с отметкой «сказано» всего {сказать}, ожидается не меньше десяти")
    # Карточки ключевых игроков — тоже реплики пульта (правило Albert Kaunitz от 29.08.2026
    # по итогам первого боевого эфира): каждого игрока отмечаем отдельно, иначе проговорённый
    # остаётся в списке и мешает искать следующего.
    игроки = re.findall(r'data-say="игрок: ([^"]+)"', html)
    if len(игроки) < 6:
        errors.append(f"пульт эфира: карточек игроков с отметкой всего {len(игроки)}, ожидается не меньше шести")
    if len(set(игроки)) != len(игроки):
        повторы = sorted(и for и in set(игроки) if игроки.count(и) > 1)
        errors.append(f"пульт эфира: одинаковый ключ отметки у игроков {повторы}: отметка одного погасит другого")
    if re.search(r'class="kv__label">\u2116\d', html):
        errors.append("ключевые игроки собраны через kv(): отметок эфира у них не будет, нужен players()")
    # Плашка роли в протоколе — это амплуа или должность, а не заглушка (уроки эфира
    # 29.08.2026): «запас» повторяет заголовок группы и не говорит комментатору ничего,
    # а голый диапазон лет без роли («тренер 1990-2018») не читается вовсе.
    роли = re.findall(r'class="pr-role">([^<]+)</span>', html)
    заглушки = sorted({р for р in роли if р.strip().lower() in ("запас", "запасной", "игрок", "-", "")})
    if заглушки:
        errors.append(f"протокол: в колонке амплуа стоит заглушка {заглушки}, нужна позиция игрока")
    годы = sorted({р for р in роли if re.search(r'\b(19|20)\d\d\b', р)})
    if годы:
        errors.append(f"протокол: в роли стоят годы {годы}. Плашка говорит, кто человек на ЭТОМ матче; "
                      f"биография ему не место, её раскрывают в карточке или углу подачи")
    длинные = sorted({р for р in роли if len(р) > 30})
    if длинные:
        errors.append(f"протокол: роль длиннее тридцати знаков {длинные}: плашка наедет на соседнее имя")
    for кусок in ("brief-said:", "say-btn", "sayCount", "resetSaid"):
        if кусок not in html:
            errors.append(f"пульт эфира: в странице нет «{кусок}», отметки работать не будут")
    # Дизайн-код матча (правило Albert Kaunitz от 28.08.2026): палитра снимается с официальных
    # сайтов обеих команд и объявляется профилем. Без объявления бриф уедет в цветах прошлого
    # матча, и заметит это только владелец.
    if not re.search(r"<!--\s*identity:\s*clients/[^>]+\.json\s*-->", html):
        errors.append("дизайн-код матча: не объявлен профиль палитры «<!-- identity: clients/<матч>.json -->»")
    for чужой in ("#A4D639", "#a4d639", "164,214,57"):
        if чужой in html:
            errors.append(f"дизайн-код матча: в стиле остался цвет эталона футбольной лиги ({чужой})")
    if "--home:" not in html or "--away:" not in html:
        errors.append("дизайн-код матча: нет разделения сторон (--home / --away), хозяева и гости не различаются цветом")
    # Баланс скобок в CSS. Одна потерянная закрывающая у @media роняет весь стиль ниже
    # внутрь мобильного блока: на широком экране правила молча перестают работать,
    # а страница при этом выглядит «почти нормально». Поймано 28.08.2026 на таблице.
    стиль = re.search(r"<style>(.*?)</style>", html, re.S)
    if not стиль:
        errors.append("в странице нет тега <style>")
    else:
        баланс = стиль.group(1).count("{") - стиль.group(1).count("}")
        if баланс != 0:
            errors.append(f"баланс скобок в CSS нарушен: незакрытых блоков {баланс}. "
                          f"Правила ниже точки разрыва не применяются")
    if "Шанс есть всегда" in html:
        errors.append("слоган «Шанс есть всегда» запрещён в производстве памяток")
    if html.count("<div") != html.count("</div>"):
        errors.append(f"баланс div нарушен: открыто {html.count('<div')}, закрыто {html.count('</div>')}")
    # Остатки прошлого матча ищем в каркасе страницы: заголовок, вкладки, подписи картинок,
    # шапки блоков. В тексте чужой клуб упоминаться может законно (биография игрока),
    # поэтому сплошной поиск по всему файлу дал бы ложную тревогу.
    frame = " ".join(re.findall(r'<title>.*?</title>|data-tab="[^"]*"|data-panel="[^"]*"|alt="[^"]*"'
                               r'|class="tab[^"]*">[^<]*|class="pr-head__name">[^<]*'
                               r'|class="match-card__team-name">[^<]*|class="site-header__title">[^<]*', html, re.S))
    for chunk in ["ЦСКА","Рубин","Ахмат","Сочи","Терек","Электрон","Экспресс","ЮФЛ","МФЛ"]:
        if chunk in frame:
            errors.append(f"остаток прошлого матча в каркасе страницы: {chunk}")
    if errors:
        raise SystemExit("СБОРКА ОСТАНОВЛЕНА:\n  - " + "\n  - ".join(errors))
    return html

out = "/Users/Rapido/Desktop/12 НЕДЕЛЬ/Комментаторство/5_Инструменты-песочница/match-briefs/2026-08-29-krasny-yar-vva/index.html"
open(out,"w",encoding="utf-8").write(gate(HTML))
print("Собрано:", len(HTML), "символов →", out)
