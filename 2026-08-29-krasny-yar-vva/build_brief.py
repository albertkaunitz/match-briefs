# -*- coding: utf-8 -*-
# Справка комментатора: «Красный Яр» · ВВА-Подмосковье, 12 тур ЧР по регби, 29.08.2026.
# Дизайн-код эталона (Электрон/ЦСКА) 1:1: style и классы взяты как есть, изменены только данные.
# Отличие от футбольных сборок: слой «Протокол» опирается на регбийную нумерацию 1..23 (номер = позиция).
import os, re, base64

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
def b64(p): return base64.b64encode(open(os.path.join(ENGINE,"logos",p),"rb").read()).decode()
KY_L  = "data:image/png;base64,"+b64("ky.png")
VVA_L = "data:image/png;base64,"+b64("vva.png")

RUGBY = "https://rugby.ru/seasons/chempionat-rossii-2026/"
YAR   = "http://yarrugby.ru/news/"
VVAS  = "https://vva-podmoskovie.ru/news/"

# ---------- конструкторы блоков эталона ----------
def angle(label, fact_, quote, src, href, hint=""):
    return f'''<details class="acc"><summary><span class="acc__title">{label}</span><span class="acc__hint">{hint}</span></summary><div class="acc__body">
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
    return f'''<details class="acc"><summary><span class="acc__title"><span class="fact__num">{num}</span>{label}</span><span class="acc__hint">{hint}</span></summary><div class="acc__body">
      <div class="fact__data">{data}</div>
      <div class="fact__phrase">{phrase}</div>
      <div class="fact__source"><a href="{href}" target="_blank" rel="noopener">{src}&nbsp;↗</a></div>
      </div></details>'''

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
 angle("Ротация: кому дают шанс",
       "Перед этими двумя турами тренер обещал ротацию «в разумных пределах». В матче со «Славой» шанс получили Владимир Чабан, Александр Елисеев и Даниил Семёнов, и все трое отметились: Чабан занёс попытку, Елисеев занёс первую за основу, Семёнов реализовал.",
       "«Тем, кто выходит сегодня из глубины состава, этот матч нужен лично: другого окна перед плей-офф не будет».",
       "отчёт клуба, 23.08", "http://yarrugby.ru/news/krasnyy-yar-obygral-slavu-mar-s-bonusom-ataki%20%2023.htm", "Чабан, Елисеев, Семёнов"),
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

h2h = "".join([
 mrow("15.05.2026","3 тур","Монино","ВВА-Подмосковье","32 : 40","Красный Яр","В"),
])

ky_form = "".join([
 mrow("12.06","6 тур","в гостях","Локомотив","19 : 57","Красный Яр","В"),
 mrow("28.06","7 тур","дома","Красный Яр","24 : 25","Динамо","П"),
 mrow("09.08","9 тур","дома","Красный Яр","13 : 17","Стрела-Ак Барс","П"),
 mrow("16.08","10 тур","в гостях","Енисей-СТМ","30 : 29","Красный Яр","П"),
 mrow("23.08","11 тур","дома","Красный Яр","45 : 10","Слава МАР","В"),
])

vva_form = "".join([
 mrow("13.06","6 тур","в гостях","Стрела-Ак Барс","45 : 26","ВВА-Подмосковье","П"),
 mrow("04.07","8 тур","дома","ВВА-Подмосковье","15 : 14","Слава МАР","В"),
 mrow("08.08","9 тур","в гостях","Динамо","68 : 7","ВВА-Подмосковье","П"),
 mrow("15.08","10 тур","в гостях","Локомотив","55 : 22","ВВА-Подмосковье","П"),
 mrow("22.08","11 тур","дома","ВВА-Подмосковье","5 : 49","Енисей-СТМ","П"),
])

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
 fact("03","Аллен Де Вит: капитан, попытка и жёлтая",
      "Восьмой номер и капитан открыл счёт попыткой на 3-й минуте и получил жёлтую карточку на 37-й.",
      "Капитан хозяев играет на грани: заносит первым и удаляется тоже.",
      "отчёт клуба, 23.08", "http://yarrugby.ru/news/krasnyy-yar-obygral-slavu-mar-s-bonusom-ataki%20%2023.htm", "№8, капитан"),
 fact("04","Дисциплина: ноль штрафных ударов соперника из игры",
      "В матче 11 тура «Красный Яр» не позволил сопернику пробить ни одного результативного штрафного, кроме одного на 8-й минуте.",
      "Тренер прямо называет дисциплину тем, чего не хватило в трёх поражениях от лидеров.",
      "отчёт клуба, 23.08", "http://yarrugby.ru/news/krasnyy-yar-obygral-slavu-mar-s-bonusom-ataki%20%2023.htm", "цена нарушений"),
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
KY_XV = {1:"Михеил Ратиашвили",2:"Бека Мамрикишвили",3:"Мхлели Дламини",4:"Данил Лосенков",5:"Виктор Архип",
 6:"Анеле Лунгиса",7:"Александр Елисеев",8:"Аллен Де Вит (к)",9:"Руди Ван Ройен",10:"Джейсон Таумалоло",
 11:"Владимир Чабан",12:"Эрлл Даури",13:"Павел Фиц",14:"Ислам Абдулкадиров",15:"Дмитрий Сухин"}
VVA_XV = {1:"Александр Новик",2:"Грант Товмасян",3:"Кирилл Собачкин",4:"Никита Арлашов",5:"Никита Акулинчев",
 6:"Александр Шахов",7:"Владислав Фризен",8:"Михаил Жлутков",9:"Александр Казаков (к)",10:"Егор Кулешов",
 11:"Дмитрий Пастернак",12:"Сергей Мотов",13:"Станислав Шмелев",14:"Дмитрий Дрождин",15:"Даниил Крылаткин"}
KY_BENCH = {16:"Шамиль Магомедов",17:"Валерий Морозов",18:"Евгений Пронин",19:"Владимир Арлашов",
 20:"Йохан Ретиф",21:"Хушнуд Сангинов",22:"Даниил Семёнов",23:"Лоуренс Преториус"}
VVA_BENCH = {16:"Александр Иванов",17:"Иван Нежданов",18:"Данил Зяблицев",19:"Владислав Капустянский",
 20:"Игорь Гаврилов",21:"Максим Агафонов",22:"Джурабек Джураев",23:"Сергей Тришин"}

pack   = [prow(n, POS[n], KY_XV[n], n, POS[n], VVA_XV[n]) for n in range(1,9)]
halves = [prow(n, POS[n], KY_XV[n], n, POS[n], VVA_XV[n]) for n in range(9,11)]
backs  = [prow(n, POS[n], KY_XV[n], n, POS[n], VVA_XV[n]) for n in range(11,16)]
bench  = [prow(n, "запас", KY_BENCH[n], n, "запас", VVA_BENCH[n]) for n in range(16,24)]

STAFF_MAIN = "".join([
 '<div class="pr-row pr-row--staff"><span class="pr-side pr-side--home"><span class="pr-role">главный тренер</span><span class="pr-name pr-name--accent">Ульрих Бейерс</span></span><span class="pr-side pr-side--away"><span class="pr-name pr-name--accent">Андрей Сорокин</span><span class="pr-role">врио главного тренера</span></span></div>',
 '<div class="pr-row pr-row--staff"><span class="pr-side pr-side--home"><span class="pr-role">тренер нападающих</span><span class="pr-name">Руан Смит</span></span><span class="pr-side pr-side--away"><span class="pr-name">Николай Неруш</span><span class="pr-role">в штабе, тренер 1990-2018</span></span></div>',
])
STAFF_REST = "".join([
 '<div class="pr-row"><span class="pr-side pr-side--home"><span class="pr-role">клуб</span><span class="pr-name">АНО «Спортивный регбийный клуб „Красный Яр“», Красноярск</span></span><span class="pr-side pr-side--away"><span class="pr-name">РК «ВВА-Подмосковье», Монино, Новинское шоссе, стр. 9</span><span class="pr-role">клуб</span></span></div>',
 '<div class="pr-row"><span class="pr-side pr-side--home"><span class="pr-role">штаб</span><span class="pr-name">Ульрих Бейерс, Руан Смит</span></span><span class="pr-side pr-side--away"><span class="pr-name">Горошилов, Кузин, Кукишев, Кушнарев В., Неруш, Сорокин, Хрокин</span><span class="pr-role">штаб</span></span></div>',
])

# ---------- Вкладка «Регби в эфире» ----------
score_rules = kv([
 ("Попытка, 5 очков","Мяч приземлён в зачётной зоне соперника. Главное событие матча и единственный способ получить бонусное очко: четыре попытки за игру дают команде дополнительный балл в таблицу."),
 ("Реализация, 2 очка","Удар по воротам с подставки сразу после попытки. Мяч должен пройти между стоек и над перекладиной. Бьют с точки напротив места приземления, поэтому попытка под штангами дороже попытки у флажка."),
 ("Штрафной удар, 3 очка","Назначается за нарушение. Команда может выбрать удар по воротам, и тогда это три очка, либо разыграть, отправив мяч в аут и получив коридор у зачётной зоны."),
 ("Дроп-гол, 3 очка","Удар по воротам с игры: мяч сначала опускают на землю, затем бьют с отскока. Редкий и эффектный способ, в этом сезоне у ВВА его исполнял Даниил Крылаткин."),
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
    <div class="site-header__title">Чемпионат России по регби · 12 тур</div>
  </div>

  <div class="stale" id="staleWarn"></div>

  <div class="tour-header">
    <h1 class="tour-header__title">Чемпионат России по регби 2026 · 12-й тур</h1>
    <div class="tour-header__meta">
      <span class="tour-header__meta-item">Регулярный чемпионат · 7 команд</span>
      <span class="tour-header__meta-item">Онлайн-эфир</span>
    </div>
  </div>

  <div class="match-card">
    <div class="match-card__location">📍 Стадион «Красный Яр», ул. Маерчака, 57, Красноярск</div>
    <div class="match-card__main">
      <div class="match-card__team"><img src="{KY_L}" alt="Красный Яр"><div class="match-card__team-name">Красный Яр</div><div class="match-card__team-city">4-е место · 21 очко</div></div>
      <div class="match-card__center"><div class="match-card__date">29 августа</div><div class="match-card__weekday">суббота</div><div class="match-card__time">13:00 мск</div></div>
      <div class="match-card__team"><img src="{VVA_L}" alt="ВВА-Подмосковье"><div class="match-card__team-name">ВВА-Подмосковье</div><div class="match-card__team-city">6-е место · 8 очков</div></div>
    </div>
    <div class="match-card__footer"><strong>Формат</strong> онлайн-эфир · 17:00 по местному времени, Красноярск это Москва плюс четыре часа</div>
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
      <details class="acc"><summary><span class="acc__title">Ключевые игроки</span><span class="acc__hint">по составу на 11 тур</span></summary><div class="acc__body">{kv([
        ("№8 · восьмой, капитан","Аллен Де Вит: попытка и жёлтая карточка в матче со «Славой»"),
        ("№10 · флай-хав","Джейсон Таумалоло: четыре реализации в последнем матче"),
        ("№2 · хукер","Бека Мамрикишвили: попытка на 30-й минуте"),
        ("№15 · фуллбэк","Дмитрий Сухин: попытка на 35-й минуте"),
        ("№3 · столб","Мхлели Дламини: новичок первой линии, тренер защищает его от критики"),
        ("№7 · фланкер","Александр Елисеев: первая попытка за основу 23 августа"),
      ])}</div></details>
      {ky_facts}
    </div>
  </div>

  <!-- ВВА -->
  <div class="panel" data-panel="vva">
    <div class="section-divider">ВВА-Подмосковье · 6-е место, 8 очков</div>
    <div style="padding:14px 16px">
      <div class="on-air"><div class="on-air__label">Кто это</div><p>Военлёты из Монино, девятикратные чемпионы СССР, сегодня шестые из семи. Две победы за сезон, ноль бонусных очков и минус 268 по разнице. Командой с 2024 года руководит врио главного тренера Андрей Сорокин.</p></div>
      <details class="acc" open><summary><span class="acc__title">Форма · последние 5 матчей</span><span class="acc__hint">П-В-П-П-П</span></summary><div class="acc__body"><div class="matches-list">{vva_form}</div></div></details>
      <details class="acc"><summary><span class="acc__title">Ключевые игроки</span><span class="acc__hint">по составу на 11 тур</span></summary><div class="acc__body">{kv([
        ("№9 · скрам-хав, капитан","Александр Казаков: бьёт штрафные и реализации, 12 очков за тайм со «Стрелой»"),
        ("№15 · фуллбэк","Даниил Крылаткин: дроп-гол и реализации"),
        ("№8 · восьмой","Михаил Жлутков: постоянный игрок стартового состава весь сезон"),
        ("№6 · фланкер","Александр Шахов: попытка в матче со «Стрелой»"),
        ("№14 · крыло","Дмитрий Дрождин: сквозной игрок задней линии"),
        ("№22 · запас","Джурабек Джураев: попытка в победном матче со «Славой»"),
      ])}</div></details>
      {vva_facts}
    </div>
  </div>

  <!-- ПРОТОКОЛ -->
  <div class="panel" data-panel="protocol">
    <div class="protocol-section-title">Протокол: кто под каким номером</div>
    <div class="pr-head">
      <div class="pr-head__side" style="flex-direction:row;align-items:center;gap:8px"><img src="{KY_L}" alt="Красный Яр" style="width:30px;height:30px;object-fit:contain"><div><div class="pr-head__name">Красный Яр</div><div class="pr-head__city">4-е место</div></div></div>
      <div class="pr-head__center">составы на 11 тур</div>
      <div class="pr-head__side pr-head__side--away" style="flex-direction:row;align-items:center;gap:8px;justify-content:flex-end"><div style="text-align:right"><div class="pr-head__name">ВВА-Подмосковье</div><div class="pr-head__city">6-е место</div></div><img src="{VVA_L}" alt="ВВА" style="width:30px;height:30px;object-fit:contain"></div>
    </div>
    <div style="padding:10px 16px 0"><div class="standings-mini__note" style="border:none;padding:0 0 8px">Это составы на предыдущий тур, 22 и 23 августа. Оба клуба публикуют состав на матч за сутки: составы на 29 августа появятся 28 августа, тогда строки заменяются. Номер в регби это позиция, поэтому таблица работает как навигация даже до объявления составов.</div></div>
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
      <ul class="checklist-live">
        <li class="check--pending"><span class="check-badge check-badge--pending">⏳</span><span class="check-text">Стартовые составы обеих команд на 29 августа<span class="check-source">клубы публикуют за сутки: yarrugby.ru и vva-podmoskovie.ru, 28 августа</span></span></li>
        <li class="check--pending"><span class="check-badge check-badge--pending">⏳</span><span class="check-text">Главный судья матча<span class="check-source">«Красный Яр» объявляет арбитра накануне отдельной новостью</span></span></li>
        <li class="check--pending"><span class="check-badge check-badge--pending">⏳</span><span class="check-text">Ссылка на трансляцию<span class="check-source">предыдущий домашний матч шёл на портале sports.ru, ссылку клуб даёт в день игры</span></span></li>
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
    <div class="site-footer__copyright" style="text-align:center">Справка комментатора · разработана по методике MKD AI Boutique · источники: rugby.ru, yarrugby.ru, vva-podmoskovie.ru (официальные)</div>
    <div class="site-footer__private" style="text-align:center">Официальные данные на 26.08.2026, 08:00. Стартовые составы, арбитр и ссылка на трансляцию добавляются 28 августа.</div>
  </div>
</div>

<script>
{SCRIPTS}
</script>
'''

HTML = f'''<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Справка комментатора · Красный Яр · ВВА-Подмосковье · ЧР по регби, 12 тур · 29.08.2026</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
{STYLE}
/* Регбийная таблица шире футбольной на две колонки: РИО и бонусные очки.
   Дизайн-код эталона не меняется, правится только сетка строки под 10 колонок. */
.standings-mini__head,.standings-mini__row{{grid-template-columns:22px 1fr 26px 24px 24px 24px 62px 44px 26px 30px;}}
@media (max-width:520px){{.standings-mini__head,.standings-mini__row{{font-size:10px;grid-template-columns:18px 1fr 20px 18px 18px 18px 50px 36px 20px 24px;padding:7px 8px;}}}}
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
    if "Шанс есть всегда" in html:
        errors.append("слоган «Шанс есть всегда» запрещён в производстве памяток")
    if html.count("<div") != html.count("</div>"):
        errors.append(f"баланс div нарушен: открыто {html.count('<div')}, закрыто {html.count('</div>')}")
    for chunk in ["ЦСКА","Рубин","Ахмат","Сочи","Терек","Электрон","Экспресс"]:
        if chunk in html:
            errors.append(f"остаток прошлого матча в шаблоне: {chunk}")
    if errors:
        raise SystemExit("СБОРКА ОСТАНОВЛЕНА:\n  - " + "\n  - ".join(errors))
    return html

out = "/Users/Rapido/Desktop/12 НЕДЕЛЬ/Комментаторство/5_Инструменты-песочница/match-briefs/2026-08-29-krasny-yar-vva/index.html"
open(out,"w",encoding="utf-8").write(gate(HTML))
print("Собрано:", len(HTML), "символов →", out)
