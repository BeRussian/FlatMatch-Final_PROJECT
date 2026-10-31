# 🚀 FlatMatch – Stage 2 Master Execution Plan & Checklist (`TASKS.md`)

> **🤖 הנחיות הפעלה לסוכן ה-AI (Antigravity / Coding Agent):**
> מסמך זה הוא מפרט הביצוע (Execution Spec) המלא והמחייב לשלב 2 של פרויקט **FlatMatch**.
>
> **כללי ברזל לסוכן:**
> 1. **שמירה על שלב 1:** אין לשבור שום התנהגות קיימת משלב 1 (`models.py`, `repository.py`, `processing.py`, `iterators.py`, `context_managers.py`). מותר להרחיב, לפצל קבצים ולעדכן תיעוד.
> 2. **עבודה סדרתית ו-Commits:** בצע כל חלק לפי הסדר (Part 0 עד Part 10). בסיום כל חלק, הרץ `pytest`, סמן `[x]` בתיבות הסימון הרלוונטיות בקובץ זה, ובצע `git commit` עם ההודעה המדויקת המופיעה בסוף החלק.
> 3. **שפה וסטנדרט קוד:** כל הקוד, שמות המשתנים, ה-Docstrings, הלוגים והדפסות ה-CLI ב-`main.py` ייכתבו באנגלית תקנית ונקייה. סעיף "שלב 2" ב-`README.md` ייכתב לפי דרישות סעיף 7.2.
> 4. **גבולות גזרה:** אין להוסיף ממשק גרפי (GUI), אתר אינטרנט, מסד נתונים חיצוני או העלאה לענן.
> 5. **חובת תיעוד AI (`AI_USAGE.md`):** בכל שלב שבו נעשה שימוש ב-AI, עדכן את `AI_USAGE.md` לפי סעיף 7.3 (תוכנית ומקרי בדיקה לפני קוד, תוצאות צפויות שהוגדרו מראש, מה הציע הכלי, מה אומת ומה תוקן).

---

## 📊 טבלת מעקב התקדמות מהירה (Progress Overview)

| חלק | נושא | קבצים מרכזיים | ניקוד במחוון | סטטוס |
| :--- | :--- | :--- | :--- | :--- |
| **Part 0** | תשתית, תלויות, סודות ולוגים | `pyproject.toml`, `.env.example`, `flatmatch/config.py` | חובה | Completed |
| **Part 1** | תכנון ההרחבה העסקית | `README.md` | 10 נק' | Completed |
| **Part 2** | חיבור לשירות חיצוני, שגיאות ו-Retry | `flatmatch/models.py`, `flatmatch/api_client.py` | 20 נק' | Pending |
| **Part 3** | תבניות תכנון והזרקת תלויות (DI) | `strategies.py`, `factories.py`, `observers.py`, `services.py` | 20 נק' | Pending |
| **Part 4** | מקביליות וסנכרון (Async + Threads/Lock) | `async_processing.py`, `threaded_processing.py` | 20 נק' | Pending |
| **Part 5** | אינטגרציית תת-מערכת ודוח עסקי משולב | `flatmatch/reports.py`, `flatmatch/services.py` | משולב | Pending |
| **Part 6** | פיתוח יכולת ב-TDD (Red -> Green -> Refactor) | `tests/test_tdd_feature.py`, `flatmatch/services.py` | 25 נק' (עם 7) | Pending |
| **Part 7** | חבילת בדיקות אוטומטיות מלאה (20+ מקרים) | `tests/test_*.py` | 25 נק' | Pending |
| **Part 8** | תסריט הדגמה מרכזי (Offline + Live API) | `main.py` | חובה | Pending |
| **Part 9** | תיעוד סופי (`README.md` + `AI_USAGE.md`) | `README.md`, `AI_USAGE.md` | 5 נק' | Pending |
| **Part 10** | בדיקת שער סופית לפני הגשה | כל המאגר | 100 נק' | Pending |

---

## 🛠️ Part 0: הכנת תשתית, תלויות והגדרות סביבה (סעיפים 2.3, 7.1)

**מיקום:** `pyproject.toml`, `.gitignore`, `.env.example`, `flatmatch/config.py`, `data/sample_data.jsonl`

### 0.1 עדכון תלויות ב-`pyproject.toml`
- [x] הוסף `requests` תחת `dependencies`.
- [x] הוסף `pytest` תחת `dependencies` (או תחת `project.optional-dependencies`).

### 0.2 קובצי סביבה ואבטחת סודות (`.gitignore` ו-`.env.example`)
- [x] ודא ש-`.gitignore` בשורש המאגר חוסם במפורש: `.env`, `.pytest_cache/`, ו-`__pycache__/`.
- [x] צור קובץ `.env.example` בשורש המאגר עם שמות משתנים וערכי דוגמה בלבד (ללא סודות אמיתיים):

```env
FLATMATCH_API_BASE_URL=https://router.project-osrm.org/route/v1/driving
FLATMATCH_API_TIMEOUT=5
FLATMATCH_API_MAX_RETRIES=3
FLATMATCH_API_RETRY_DELAY=0.5
FLATMATCH_API_KEY=example_optional_key_do_not_use_real_secret
```

### 0.3 יצירת מודול הגדרות ולוגים (`flatmatch/config.py`)
- [x] טען משתני סביבה באמצעות `os.getenv` עם ערכי ברירת מחדל בטוחים (ותמיכה בטעינת `.env` אם קיים, ללא חשיפת סודות).
- [x] הגדר קבועים:
  - `API_BASE_URL`
  - `API_TIMEOUT = 5`
  - `MAX_RETRIES = 3`
  - `RETRY_DELAY = 0.5`
  - `CITY_COORDINATES`: מילון קואורדינטות `(lon, lat)` עבור הערים הנתמכות (`Tel Aviv`, `Jerusalem`, `Haifa`, `Ramat Gan`, `Beer Sheva`, `Herzliya`).
- [x] הגדר פונקציה `get_logger(name: str) -> logging.Logger` המתעדת פעולות וכשלים בפורמט אחיד, **ללא חשיפת סודות (`API_KEY`) או מידע אישי רגיש**.

### 0.4 וידוא נתוני ההדגמה ב-`data/sample_data.jsonl`
- [x] ודא שכל 20 הרשומות ב-`data/sample_data.jsonl` הן סינתטיות לחלוטין (ללא מידע אישי אמיתי) ונטענות ללא שגיאות.

### 🔖 Git Commit – Part 0
```bash
git add pyproject.toml .gitignore .env.example flatmatch/config.py TASKS.md
git commit -m "chore(config): add stage 2 dependencies, env example, and logging config"
```

---

## 🎯 Part 1: תכנון ההרחבה העסקית (סעיף 1 במחוון)

> **הנחיה לסוכן:** סעיף זה מגדיר את הארכיטקטורה העסקית שתמומש בקוד ותתועד ב-`README.md` (תחת סעיף 7.2).

- [x] **1.1 התהליך העסקי המורחב והערך שלו:**
  - הרחבת תהליך סינון ודירוג הדירות של `FlatMatch` משלב 1: מעבר לתקציב, עיר והעדפות סגנון חיים (`Preferences`), המערכת מחשבת כעת את **מרחק הנסיעה וזמן ההגעה (Commute Duration & Distance)** מהדירה של ה-`RoommateSeeker` אל מרכז היעד המבוקש של ה-`ApartmentSeeker`.
  - **הערך העסקי:** מניעת התאמות שבהן הדירה עומדת בתקציב אך דורשת נסיעה יומית ארוכה מדי, ושקלול זמן הנסיעה ישירות בציון ההתאמה (`Match Score`), בסינון המועמדים ובדוח העסקי.
- [x] **1.2 המידע מהשירות החיצוני והשימוש בו:**
  - **השירות החיצוני:** **OSRM (Open Source Routing Machine) Public API**
    - כתובת: `GET https://router.project-osrm.org/route/v1/driving/{lon1},{lat1};{lon2},{lat2}?overview=false`
  - **המידע המתקבל:** JSON המכיל `code` ורשימת `routes` עם שדות `distance` (במטרים) ו-`duration` (בשניות).
  - **שימוש במערכת:** המרה לאובייקט מערכת `CommuteMetrics(origin_city, destination_city, distance_km, duration_minutes, is_verified)`. משמש ב-`services.py` לחישוב ציון התאמה, פסילת דירות שחורגות מזמן נסיעה מקסימלי (`max_commute_minutes`), ועדכון תת-המערכת והדוח.
- [x] **1.3 התנהגות המערכת בכשל שירות חיצוני או מידע לא תקין:**
  - `api_client.py` זורק חריגה ספציפית ומתעד בלוג לאחר מיצוי ניסיונות ה-Retry (בכשל תקשורת) או מיד (בשגיאת HTTP / JSON / מבנה נתונים).
  - `services.py` תופס את החריגה ועובר ל**מצב גיבוי מבוקר (Graceful Fallback)**: מחזיר `CommuteMetrics(..., distance_km=0.0, duration_minutes=0.0, is_verified=False)` ומסמן סטטוס `"FALLBACK_UNVERIFIED"` (ותת-המערכת מסמנת `"PENDING_MANUAL_VERIFICATION"`), כך שהמערכת לא קורסת ולא מאשרת חוזה שגוי.
- [x] **1.4 פעולות עצמאיות בחפיפה (Async) והמשאב המשותף (Threads + Lock):**
  - **פעולות עצמאיות (`async_processing.py`):** איסוף מקבילי של נתוני זמינות ואימות תחבורה עבור **לפחות 3 דירות שונות** במקביל (כל דירה נבדקת עצמאית ללא תלות באחרות).
  - **המשאב המשותף (`threaded_processing.py`):** תפיסת החדרים הפנויים האחרונים בדירה מבוקשת (`SharedRoomInventory` עם `available_rooms` מוגבל). מוגן באמצעות `threading.Lock` למניעת Race Condition של רישום יתר (Overbooking).

---

## 🌐 Part 2: חיבור לשירות חיצוני, שגיאות ו-Retry (סעיף 2 במחוון – 20 נק')

**מיקום:** `flatmatch/models.py`, `flatmatch/api_client.py`

### 2.1 מודל נתונים לתשובת ה-API (`flatmatch/models.py`)
- [ ] הוסף מחלקה `CommuteMetrics` ב-`flatmatch/models.py`:
  - שדות: `origin_city: str`, `destination_city: str`, `distance_km: float`, `duration_minutes: float`, `is_verified: bool = True`.
  - הוסף ולידציה שמוודאת ש-`distance_km >= 0` ו-`duration_minutes >= 0` (זורקת `ValueError` אם שלילי).

### 2.2 הגדרת 4 חריגות מובחנות ב-`flatmatch/api_client.py` (סעיף 2.2)
- [ ] הגדר 4 מחלקות חריגה ברורות להבחנה בין סוגי הכשלים:
  1. `APIConnectionError(Exception)` – כשל תקשורת (`Timeout` או `ConnectionError`) לאחר מיצוי ניסיונות ה-Retry.
  2. `APIHTTPError(Exception)` – שגיאת HTTP מ-`response.raise_for_status()` (`HTTPError`, כולל שמירת `status_code` אם קיים, כגון 401, 404, 429, 503).
  3. `APIResponseFormatError(Exception)` – JSON שאינו ניתן לפענוח (`ValueError` / `json.JSONDecodeError`).
  4. `APIDataValidationError(Exception)` – נתונים שאינם תואמים למבנה הנדרש (חסר `routes`, רשימה ריקה, חסרים `distance` או `duration`, או ערכים לא חוקיים).

### 2.3 מימוש `CommuteAPIClient` ב-`flatmatch/api_client.py` (סעיפים 2.1, 2.2)
- [ ] ממש בנאי המקבל תלויות מבחוץ (עבור בדיקות קלות ללא רשת וללא המתנה):

```python
def __init__(
    self,
    base_url: str = API_BASE_URL,
    timeout: float = API_TIMEOUT,
    max_retries: int = MAX_RETRIES,
    retry_delay: float = RETRY_DELAY,
    http_get=requests.get,
    sleep_func=time.sleep,
) -> None:
```

- [ ] ממש מתודה `fetch_commute_metrics(self, origin_coords: tuple[float, float], dest_coords: tuple[float, float], origin_city: str = "", dest_city: str = "") -> CommuteMetrics`:
  - [ ] שליחת בקשת `GET` עם `params={"overview": "false"}` ו-`timeout=self.timeout`.
  - [ ] **מנגנון Retry ממוקד:**
    - עד `max_retries` (ברירת מחדל: **3 ניסיונות בסך הכול**).
    - מתבצע **אך ורק** על `requests.exceptions.Timeout` או `requests.exceptions.ConnectionError`.
    - בין ניסיונות: תיעוד ב-`logger.warning` והמתנה באמצעות `self.sleep_func(self.retry_delay)`.
    - לאחר הכישלון בניסיון ה-3: תיעוד ב-`logger.error` וזריקת `APIConnectionError` ברורה.
  - [ ] **בדיקת קוד התגובה:** קריאה ל-`response.raise_for_status()`. אם נזרקת `HTTPError`, תיעוד בלוג וזריקת `APIHTTPError` מיד **ללא Retry**.
  - [ ] **פענוח JSON:** קריאה ל-`response.json()`. בכשל פענוח, תיעוד וזריקת `APIResponseFormatError` מיד **ללא Retry**.
  - [ ] **אימות שדות ומבנה:** בדיקה ש-`routes` הוא `list` לא ריק, ושבתוך `routes[0]` קיימים `distance` ו-`duration` כמספרים אי-שליליים. אם לא, זריקת `APIDataValidationError` מיד **ללא Retry**.
  - [ ] **המרה לאובייקט מערכת:** חישוב `distance_km = round(distance / 1000.0, 2)` ו-`duration_minutes = round(duration / 60.0, 2)` והחזרת `CommuteMetrics(..., is_verified=True)`.
  - [ ] **הפרדת אחריויות:** ודא שאין ב-`api_client.py` שום לוגיקה עסקית של סינון או דירוג מועמדים.

### 🔖 Git Commit – Part 2
```bash
git add flatmatch/models.py flatmatch/api_client.py TASKS.md
git commit -m "feat(api): implement CommuteAPIClient with retry logic, validation, and distinct error types"
```

---

## 🧩 Part 3: תבניות תכנון, הזרקת תלויות ושירות עסקי (סעיפים 2.1, 3 במחוון – 20 נק')

**מיקום:** `flatmatch/strategies.py`, `flatmatch/factories.py`, `flatmatch/observers.py`, `flatmatch/services.py`

### 3.1 תבנית Strategy (`flatmatch/strategies.py`)
- [ ] הגדר מחלקת בסיס אבסטרקטית `MatchingStrategy(ABC)` עם מתודה אבסטרקטית:
  `calculate_score(self, seeker: ApartmentSeeker, owner: RoommateSeeker, commute: CommuteMetrics | None = None) -> float`
- [ ] ממש חלופה 1: `BudgetFocusedStrategy(MatchingStrategy)`
  - מתעדפת חיסכון בתקציב (`seeker.max_budget - owner.apartment.rent_per_room`) והתאמת ניקיון, עם משקל נמוך לזמן הנסיעה.
- [ ] ממש חלופה 2: `CommuteAndLifestyleStrategy(MatchingStrategy)`
  - מתעדפת זמן נסיעה קצר מ-`CommuteMetrics` (בונוס על נסיעה קצרה מאומתת `is_verified=True` וקנס משמעותי על נסיעה ארוכה) וכן חפיפת `amenities`.

### 3.2 תבנית Factory (`flatmatch/factories.py`)
- [ ] ממש מחלקה `UserFactory` עם מתודה `create_user(data: dict) -> User`:
  - שימוש ב-`if/elif` לפי `data.get("type")`:
    - עבור `"apartment_seeker"` -> מחזיר `ApartmentSeeker.from_dict(data)`
    - עבור `"roommate_seeker"` -> מחזיר `RoommateSeeker.from_dict(data)`
    - עבור כל ערך אחר או חסר -> זורק `ValueError` ברור.
- [ ] עדכן את `flatmatch/repository.py` כך שישתמש ב-`UserFactory.create_user(record)` במקום בדיקות סוג ישירות.

### 3.3 תבנית Observer (`flatmatch/observers.py`)
- [ ] הגדר ממשק אבסטרקטי `MatchEventListener(ABC)` עם מתודה `on_match_evaluated(self, event_data: dict) -> None`.
- [ ] ממש מגיב 1: `MatchStatisticsObserver(MatchEventListener)`
  - שומר ומעדכן מונים: `total_evaluated`, `verified_commutes`, `api_fallbacks`, ו-`approved_by_city: dict[str, int]`.
- [ ] ממש מגיב 2: `ApplicantNotificationObserver(MatchEventListener)`
  - שומר רשימת הודעות `notifications: list[str]` ומתעד בלוג כאשר נמצאת התאמה או כאשר נדרשת בדיקה ידנית עקב כשל ב-API.

### 3.4 חיבור הרכיבים והזרקת תלויות ב-`flatmatch/services.py`
- [ ] ממש מחלקה/מבנה תוצאה `MatchEvaluationResult` (שדות: `seeker_phone`, `owner_phone`, `city`, `rent_per_room`, `score`, `commute_metrics`, `status`, `is_approved`).
- [ ] ממש את `FlatMatchService` עם **הזרקת תלויות דרך הבנאי (`__init__`)**:

```python
def __init__(
    self,
    api_client: CommuteAPIClient,
    strategy: MatchingStrategy,
    observers: list[MatchEventListener] | None = None,
    max_commute_minutes: float = 45.0,
) -> None:
```

- [ ] ממש מתודה `evaluate_candidate_match(self, seeker: ApartmentSeeker, owner: RoommateSeeker) -> MatchEvaluationResult`:
  1. בודקת Dealbreakers בסיסיים (`seeker.evaluate_dealbreakers(owner)`).
  2. קוראת ל-`self.api_client.fetch_commute_metrics(...)` לפי קואורדינטות עיר הדירה ועיר היעד המועדפת של המחפש.
  3. **טיפול בכשל שירות חיצוני:** תופסת `(APIConnectionError, APIHTTPError, APIResponseFormatError, APIDataValidationError)`, רושמת לוג אזהרה, ויוצרת אובייקט גיבוי `CommuteMetrics(..., distance_km=0.0, duration_minutes=0.0, is_verified=False)` עם סטטוס `"FALLBACK_UNVERIFIED"`.
  4. **החלטה וחישוב עסקי:**
     - אם `commute.is_verified` הוא `True` ו-`commute.duration_minutes > self.max_commute_minutes`: פוסלת את ההתאמה (`is_approved=False`, `status="REJECTED_COMMUTE_EXCEEDED"`).
     - מחשבת את הציון בפולימורפיזם מלא: `score = self.strategy.calculate_score(seeker, owner, commute)`.
     - מפעילה את כל ה-`self.observers` הרשומים (`observer.on_match_evaluated(event_data)`).
     - מחזירה את אובייקט ה-`MatchEvaluationResult`.

### 🔖 Git Commit – Part 3
```bash
git add flatmatch/strategies.py flatmatch/factories.py flatmatch/observers.py flatmatch/repository.py flatmatch/services.py TASKS.md
git commit -m "feat(patterns,services): add Strategy, Factory, Observer patterns and DI in FlatMatchService"
```

---

## ⚡ Part 4: מקביליות וסנכרון (סעיף 5 במחוון – 20 נק')

**מיקום:** `flatmatch/async_processing.py`, `flatmatch/threaded_processing.py`

### 4.1 איסוף מידע אסינכרוני (`flatmatch/async_processing.py` – סעיף 5.1)
- [ ] הגדר נתוני סימולציה קבועים עבור לפחות **3 משימות עצמאיות** (למשל 4 דירות: `["APT-101", "APT-102", "APT-103", "APT-104"]`), כאשר זמני ההמתנה (`delay`) שונים זה מזה (למשל `0.05s`, `0.01s`, `0.03s`, `0.02s`) כך שסדר הסיום הטבעי במקביל שונה מסדר הקלט.
- [ ] ממש פונקציה אסינכרונית למשימה בודדת:
  `async def fetch_apartment_verification_async(apt_id: str, simulated_db: dict | None = None) -> dict`
  - משתמשת אך ורק ב-`await asyncio.sleep(delay)` ומחזירה מילון נתונים עבור `apt_id`.
  - **אסור להשתמש ב-`time.sleep` או בקריאות HTTP חוסמות!**
- [ ] ממש שתי גרסאות על אותן משימות ואותם נתוני בדיקה:
  1. **גרסה סדרתית:** `async def collect_verifications_sequential(apt_ids: list[str], simulated_db: dict | None = None) -> list[dict]`
     - ממתינה (`await`) לסיום כל משימה לפני תחילת המשימה הבאה.
  2. **גרסה אסינכרונית מקבילית:** `async def collect_verifications_concurrent(apt_ids: list[str], simulated_db: dict | None = None) -> list[dict]`
     - מתזמנת את כל המשימות מראש באמצעות `asyncio.create_task` ואוספת את התוצאות באמצעות `await asyncio.gather(*tasks)`.
- [ ] ודא ששתי הפונקציות מחזירות תוצאות **זהות לחלוטין** ולפי **סדר הקלט המקורי** (`apt_ids`).

### 4.2 Threads ומשאב משותף (`flatmatch/threaded_processing.py` – סעיף 5.2)
- [ ] ממש מחלקה `SharedRoomInventory`:
  - שדות: `apartment_id: str`, `available_rooms: int`, `approved_seekers: list[str]`, ומופע `self._lock = threading.Lock()`.
- [ ] ממש מתודה `attempt_room_booking(self, seeker_name: str) -> bool`:
  - משתמשת ב-`with self._lock:` כדי להגן על רצף הבדיקה והעדכון (Check-Then-Act):
    - אם `self.available_rooms > 0`: מפחיתה `self.available_rooms -= 1`, מוסיפה את `seeker_name` ל-`self.approved_seekers`, ומחזירה `True`.
    - אחרת: מחזירה `False`.
  - **אסור לבצע קריאת רשת בתוך הקטע הנעול!**
- [ ] ממש פונקציה `run_concurrent_room_bookings(available_rooms: int, seeker_names: list[str]) -> SharedRoomInventory`:
  - יוצרת Thread עבור כל מועמד ב-`seeker_names`.
  - מפעילה את **כל** ה-Threads באמצעות `t.start()` בלולאה ראשונה.
  - ממתינה לסיום **כל** ה-Threads באמצעות `t.join()` בלולאה שנייה נפרדת.
  - מחזירה את מופע ה-`SharedRoomInventory` לבדיקת מספר האישורים והמצב הסופי.

### 🔖 Git Commit – Part 4
```bash
git add flatmatch/async_processing.py flatmatch/threaded_processing.py TASKS.md
git commit -m "feat(concurrency): implement async task collection and thread-safe room booking with Lock"
```

---

## 👥 Part 5: הרחבת אינטגרציה ודוח עסקי משולב (סעיף 6 במחוון)

**מיקום:** `flatmatch/reports.py`, `flatmatch/observers.py`, `flatmatch/services.py`

### 5.1 תת-מערכת בקרת חוזים ושיבוץ (`LeaseInspectionSubsystem`)
- [ ] ממש מחלקה `LeaseInspectionSubsystem` (ב-`flatmatch/reports.py` או `flatmatch/services.py`) המקושרת ל-`FlatMatchRepository`:
  - מוודאת שמזהי ה-`seeker_phone` וה-`owner_phone` קיימים במאגר; אם אחד מהם לא קיים, זורקת `ValueError("Invalid user link between systems")`.
  - מעדכנת רשומות שיבוץ לפי תוצאת ה-API והשירות המרכזי:
    - התאמה מאומתת ותקינה (`is_verified=True` ו-`is_approved=True`) -> סטטוס `"READY_FOR_LEASE"`.
    - חריגה מזמן נסיעה (`status == "REJECTED_COMMUTE_EXCEEDED"`) -> סטטוס `"REJECTED_HIGH_COMMUTE"`.
    - **כשל בשירות החיצוני (`is_verified=False`)** -> מונעת אישור חוזה שגוי ומגדירה סטטוס `"PENDING_MANUAL_VERIFICATION"`.
- [ ] ממש מגיב `SubsystemSyncObserver(MatchEventListener)` ב-`flatmatch/observers.py` שמעדכן אוטומטית את `LeaseInspectionSubsystem` בכל הערכת התאמה.

### 5.2 דוח עסקי משולב (`flatmatch/reports.py` – סעיף 6.3)
- [ ] ממש פונקציה `generate_integrated_business_report(repository, subsystem) -> dict`:
  - משלבת נתונים מהמאגר המרכזי ומתת-המערכת.
  - מחשבת ומחזירה **מדדים חדשים התומכים בהחלטה עסקית**:
    - `total_seekers_and_owners`: סך המשתמשים הפעילים.
    - `ready_for_lease_count`: מספר ההתאמות המאומתות המוכנות לחתימת חוזה.
    - `pending_manual_verification_count`: מספר ההתאמות התקציביות שממתינות לבדיקה ידנית עקב כשל/חוסר זמינות של שירות התחבורה.
    - `verified_ready_ratio`: יחס ההתאמות המאומתות מתוך סך הפניות שנפתחו בתת-המערכת.

### 🔖 Git Commit – Part 5
```bash
git add flatmatch/reports.py flatmatch/observers.py flatmatch/services.py TASKS.md
git commit -m "feat(reports,integration): add LeaseInspectionSubsystem, observer sync, and integrated business report"
```

---

## 🚦 Part 6: פיתוח יכולת חדשה ב-TDD מלא (סעיף 4.2 במחוון – 3 Commits נפרדים!)

**מיקום:** `tests/test_tdd_feature.py`, `flatmatch/services.py`

> **⚠️ הוראה קריטית לסוכן:** סעיף 4.2 דורש תיעוד ב-Git של מחזור TDD אמיתי (`Red` -> `Green` -> `Refactor`) עם **3 קומיטים נפרדים** שיופיעו בהיסטוריית ה-Git ויתועדו ב-`README.md`.
>
> **היכולת המפותחת ב-TDD:** `calculate_commute_adjusted_budget(base_budget: float, commute: CommuteMetrics) -> float`
> - **הדרישה העסקית:** כל דקת נסיעה מעל 20 דקות מפחיתה את תקרת התקציב האפקטיבית ב-15 ש"ח לדקה. אם `commute.is_verified` הוא `False`, מוחזר התקציב הבסיסי ללא קנס מרחק. התקציב המוחזר לא ירד מתחת ל-`0.0`.

### 6.1 שלב RED – כתיבת בדיקה נכשלת בלבד
- [ ] צור ב-`flatmatch/services.py` חתימת פונקציה ריקה `calculate_commute_adjusted_budget(base_budget: float, commute: CommuteMetrics) -> float` שזורקת `NotImplementedError`.
- [ ] צור קובץ `tests/test_tdd_feature.py` עם בדיקה `test_calculate_commute_adjusted_budget_reduces_ceiling_above_threshold` שבודקת שתקציב בסיס של `3000.0` ש"ח ונסיעה מאומתת של `30.0` דקות מחזירים בדיוק `2850.0` ש"ח.
- [ ] הרץ `pytest tests/test_tdd_feature.py` וודא שהבדיקה **נכשלת (RED)**.
- [ ] **בצע Commit ראשון של TDD (RED):**

```bash
git add tests/test_tdd_feature.py flatmatch/services.py
git commit -m "test(tdd-red): add failing test for commute-adjusted budget ceiling calculation"
```

### 6.2 שלב GREEN – מימוש מינימלי שמעביר את הבדיקה
- [ ] ממש את החישוב ב-`calculate_commute_adjusted_budget` ב-`flatmatch/services.py` כך שהבדיקה תעבור.
- [ ] הרץ `pytest tests/test_tdd_feature.py` וודא שהבדיקה **עוברת (GREEN)**.
- [ ] **בצע Commit שני של TDD (GREEN):**

```bash
git add flatmatch/services.py
git commit -m "feat(tdd-green): implement commute-adjusted budget ceiling calculation"
```

### 6.3 שלב REFACTOR – שיפור הקוד והוספת מקרי קצה
- [ ] שפר את הקוד של `calculate_commute_adjusted_budget` ב-`flatmatch/services.py`: חלץ קבועים ברורים (`FREE_COMMUTE_MINUTES = 20.0`, `PENALTY_PER_MINUTE_ILS = 15.0`), הוסף הגנה מפני `is_verified=False` והגנה מפני תקציב שלילי (`max(0.0, ...)`).
- [ ] הרחב את `tests/test_tdd_feature.py` לבדיקת מקרי הקצה (נסיעה קצרה מ-20 דקות, נסיעה לא מאומתת, ותקציב שלילי).
- [ ] הרץ `pytest tests/test_tdd_feature.py` וודא שכל הבדיקות **עוברות (REFACTOR)**.
- [ ] **בצע Commit שלישי של TDD (REFACTOR):**

```bash
git add flatmatch/services.py tests/test_tdd_feature.py TASKS.md
git commit -m "refactor(tdd-refactor): extract constants and handle unverified commute in budget adjustment"
```

---

## 🧪 Part 7: חבילת בדיקות אוטומטיות מלאה (סעיפים 4.1, 6.4 במחוון – 25 נק')

**מיקום:** תיקיית `tests/`

> **כללי ברזל לבדיקות (סעיף 4.1):**
> - לפחות **20 מקרי בדיקה משמעותיים** בסך הכול.
> - שימוש חובה ב-`@pytest.fixture`, `@pytest.mark.parametrize` (לפחות 3 מקרים), `pytest.raises`, `Mock` / `patch`, ו-`tmp_path`.
> - כל הבדיקות חייבות לרוץ **ללא רשת**, **ללא מפתח API**, ו**ללא המתנות Retry אמיתיות** (`sleep_func=Mock()`).
> - מחליפים את התלות החיצונית (`http_get` / `requests.get`), ולא את הפונקציה הנבדקת!

### 7.1 `tests/test_models.py` (שמירת שלב 1, ולידציה, `tmp_path` ו-`Factory`)
- [ ] **Case 1:** `test_stage1_models_and_dealbreakers_preserved` (שימוש ב-`@pytest.fixture`): וידוא ש-`ApartmentSeeker`, `RoommateSeeker`, ו-`evaluate_dealbreakers` משלב 1 עובדים כמצופה.
- [ ] **Case 2, 3, 4:** `test_invalid_domain_inputs_raise_value_error` (שימוש ב-`@pytest.mark.parametrize` עם לפחות 3 מצבים שונים + `pytest.raises(ValueError)`): גיל מתחת ל-18, תקציב שלילי, רמת ניקיון מחוץ ל-1..5.
- [ ] **Case 5:** `test_repository_streams_jsonl_using_tmp_path` (שימוש ב-`tmp_path`): כתיבת קובץ JSONL זמני ל-`tmp_path`, טעינתו ב-`FlatMatchRepository` ווידוא מניעת כפילויות טלפון.
- [ ] **Case 6:** `test_user_factory_creates_subclasses_and_rejects_invalid_type`: בדיקת `UserFactory` לשני סוגי המשתמשים וזריקת `ValueError` לסוג לא חוקי.
- [ ] **Case 7:** `test_apartment_hold_context_rolls_back_on_error`: וידוא ש-`ApartmentHoldContext` משלב 1 מחזיר סטטוס ל-`AVAILABLE` בעת חריגה.

### 7.2 `tests/test_api_client.py` (שירות חיצוני ו-Retry מבודדים מרשת)
- [ ] **Case 8:** `test_api_client_success_returns_commute_metrics`: החלפת `http_get` ב-`Mock` המחזיר JSON תקין (`distance: 15000, duration: 1200`), ווידוא שמתקבל `distance_km == 15.0` ו-`duration_minutes == 20.0`.
- [ ] **Case 9:** `test_api_client_timeout_retries_3_times_and_raises`: דימוי `requests.exceptions.Timeout`, החלפת `sleep_func` ב-`Mock`, ווידוא שבוצעו **בדיוק 3 ניסיונות** ונזרקה `APIConnectionError`.
- [ ] **Case 10:** `test_api_client_retry_succeeds_on_third_attempt`: דימוי `ConnectionError` בניסיונות 1 ו-2 והצלחה בניסיון 3; וידוא קבלת `CommuteMetrics` תקין.
- [ ] **Case 11:** `test_api_client_http_error_does_not_retry`: דימוי שגיאת HTTP (למשל 404/401 ב-`raise_for_status`), ווידוא שנזרקת `APIHTTPError` אחרי **ניסיון 1 בלבד** (ללא Retry).
- [ ] **Case 12:** `test_api_client_missing_required_field_raises_validation_error`: החזרת JSON ללא השדה `routes` או `duration`, ווידוא זריקת `APIDataValidationError` ללא Retry.
- [ ] **Case 13:** `test_api_client_corrupted_json_raises_format_error`: החזרת תגובה שבה `.json()` זורק `ValueError`, ווידוא זריקת `APIResponseFormatError` ללא Retry.

### 7.3 `tests/test_services.py` (לוגיקה עסקית, Strategy, Observer ו-DI)
- [ ] **Case 14:** `test_strategies_calculate_distinct_expected_scores`: השוואת `BudgetFocusedStrategy` מול `CommuteAndLifestyleStrategy` עם תוצאות מספריות קבועות מראש.
- [ ] **Case 15:** `test_observers_updated_on_candidate_evaluation`: וידוא ש-`MatchStatisticsObserver` ו-`ApplicantNotificationObserver` מתעדכנים בעת קריאה ל-`evaluate_candidate_match`.
- [ ] **Case 16:** `test_service_rejects_when_commute_exceeds_max_limit`: הזרקת Mock של `api_client` המחזיר 60 דקות נסיעה (כאשר הרף הוא 45), ווידוא שההתאמה נפסלת (`is_approved is False`).

### 7.4 `tests/test_async_processing.py` ו-`tests/test_threaded_processing.py` (מקביליות)
- [ ] **Case 17:** `test_async_concurrent_matches_sequential_and_preserves_order`: הרצת הגרסה הסדרתית והמקבילית על 4 דירות עם זמני סיום הפוכים מסדר הקלט, ווידוא זהות מלאה ושמירה על סדר הקלט.
- [ ] **Case 18:** `test_threaded_room_booking_lock_prevents_overbooking`: הרצת 6 Threads שמנסים לתפוס 2 חדרים פנויים; וידוא שרק 2 אושרו (`len(approved_seekers) == 2`) ושנותרו `0` חדרים פנויים.

### 7.5 `tests/test_integration.py` ו-`tests/test_reports.py` (4 מקרי סעיף 6.4)
- [ ] **Case 19:** `test_integrated_process_end_to_end_success` (`test_integration.py`): תהליך משולב מלא המסתיים בהצלחה ומעביר את הרשומה בתת-המערכת לסטטוס `"READY_FOR_LEASE"`.
- [ ] **Case 20:** `test_integrated_process_api_failure_prevents_false_approval` (`test_integration.py`): כשל בשירות החיצוני מעביר את המערכת למצב גיבוי ויוצר בתת-המערכת סטטוס `"PENDING_MANUAL_VERIFICATION"`.
- [ ] **Case 21:** `test_subsystem_invalid_user_link_raises_error` (`test_integration.py`): העברת מזהה משתמש שאינו קיים במאגר אל תת-המערכת זורקת `ValueError`.
- [ ] **Case 22:** `test_integrated_report_calculates_new_metrics_accurately` (`test_reports.py`): בדיקת נכונות המדדים החדשים בדוח המשולב (`ready_for_lease_count`, `pending_manual_verification_count`, `verified_ready_ratio`).

### 🔖 Git Commit – Part 7
```bash
pytest -v
git add tests/ TASKS.md
git commit -m "test(suite): add comprehensive pytest suite covering API, retries, patterns, async, threads, and integration"
```

---

## 🖥️ Part 8: עדכון `main.py` להדגמת שלב 2 (סעיפים 6.5, 7.1 במחוון)

**מיקום:** `main.py`

- [ ] **8.1 תמיכה בשני מצבי הרצה (ללא תפריט אינטראקטיבי):**
  - **ברירת מחדל (`python main.py`):** רצה מקומית לחלוטין ללא רשת וללא מפתחות, ומדפיסה בראש הפלט:
    `[MODE: OFFLINE / SIMULATED DATA - No network or API keys required]`
  - **חיבור אמיתי (`python main.py --live`):** מבצעת קריאת `GET` אמיתית ל-OSRM API, ומדפיסה בראש הפלט:
    `[MODE: LIVE NETWORK API - Fetching real routing data from OSRM]`
- [ ] **8.2 תסריט ההדגמה ב-`main.py`:**
  - טעינת המשתמשים מ-`data/sample_data.jsonl` באמצעות `UserFactory`.
  - הרצת `FlatMatchService` עם שתי האסטרטגיות (`BudgetFocusedStrategy` ו-`CommuteAndLifestyleStrategy`), ה-`Observers` ותת-המערכת `LeaseInspectionSubsystem`.
  - הדגמת תגובת המערכת גם בהצלחת API וגם בכשל API (Fallback -> `PENDING_MANUAL_VERIFICATION`).
  - הפקת והדפסת הדוח העסקי המשולב (`generate_integrated_business_report`).
  - הדגמת האיסוף האסינכרוני (`Sequential` מול `Concurrent`) והדגמת ה-Threads עם `Lock` (`SharedRoomInventory`).

### 🔖 Git Commit – Part 8
```bash
python main.py
python main.py --live
git add main.py TASKS.md
git commit -m "feat(main): add stage 2 end-to-end demonstration with offline default and --live API mode"
```

---

## 📄 Part 9: עדכון תיעוד `README.md` ו-`AI_USAGE.md` (סעיפים 7.2, 7.3 במחוון)

**מיקום:** `README.md`, `AI_USAGE.md`

### 9.1 עדכון `AI_USAGE.md` (סעיף 7.3)
- [ ] הוסף פרק `## Stage 2 – Responsible AI Usage` בקובץ `AI_USAGE.md` בלבד, הכולל:
  - תיעוד בקשת תוכנית ומקרי בדיקה לפני כתיבת קוד.
  - פירוט **לפחות שני מקרים** שבהם הגדרנו בעצמנו את התוצאות הצפויות מראש (חישוב תקרת התקציב ב-TDD וחישוב ציוני האסטרטגיות).
  - תיעוד מה הציע ה-AI, מה אומת מול הבדיקות, ומה תוקן.

### 9.2 עדכון `README.md` תחת כותרת אחת `## שלב 2` (סעיף 7.2)
- [ ] שמור על תוכן שלב 1 הקיים, והוסף בסופו כותרת `## שלב 2` הכוללת **בדיוק את 5 תתי-הסעיפים הבאים** בנקודות קצרות:
  1. **מה נוסף בשלב 2?** – ההרחבה העסקית (OSRM Commute API), הערך העסקי, תת-המערכת המשולבת (`LeaseInspectionSubsystem`), התהליך המשותף והמדד החדש בדוח.
  2. **איך מריצים?** – גרסת Python, התקנת תלויות, משתני סביבה (`.env.example` ללא סודות), פקודה להרצה ללא רשת (`python main.py`), פקודה להרצה מול השירות האמיתי (`python main.py --live`), ופקודה להרצת הבדיקות (`pytest -v`).
  3. **איך הקוד מאורגן?** – עץ תיקיות מעודכן, שורה על תפקיד כל מודול מרכזי, מיקום תת-המערכת וארבע הבדיקות הנוספות, וחלוקת אחריות קצרה בצוות.
  4. **החלטות תכנון מרכזיות:**
     - השירות החיצוני (OSRM API) + קישור לתיעודו, השימוש העסקי במידע, וטיפול ב-4 סוגי הכשלים, ה-Retry ומצב הגיבוי.
     - תבניות התכנון שנבחרו (`Strategy`, `Factory`, `Observer`) והסיבה לבחירתן.
     - כיצד העברת תלויות מבחוץ (DI בבנאי) מסייעת להפרדת אחריויות ולבדיקה מבודדת.
     - המשימות העצמאיות ב-Async, המשאב המשותף ב-Threads (`SharedRoomInventory`), ואיזו שגיאה מונע ה-`Lock` (Race Condition מסוג Check-Then-Act המוביל לרישום יתר לחדר האחרון).
     - זרימת המידע בין המערכת המרכזית לתת-המערכת, התגובה לכשל, והתבנית המשרתת את השילוב (`Observer`).
  5. **הוכחות שהמערכת עובדת:**
     - סיכום תוצאות הבדיקות (`pytest`).
     - דוגמת חיבור אמיתי (`python main.py --live`) ותוצאתו.
     - הפניות ל-Commit Hashes המדויקים של `Red`, `Green`, `Refactor` בציון היכולת שפותחה ב-TDD (`calculate_commute_adjusted_budget`).

### 🔖 Git Commit – Part 9
```bash
git add README.md AI_USAGE.md TASKS.md
git commit -m "docs(stage2): complete README stage 2 section, TDD commit references, and AI_USAGE"
```

---

## ✅ Part 10: בדיקת שער סופית לפני הגשה (Submission Verification Gate)

- [ ] `pytest -v` עובר ב-100% (לפחות 22 בדיקות עוברות ללא רשת וללא המתנות אמיתיות).
- [ ] `python main.py` רץ ללא שגיאות ללא רשת ומדפיס שהמידע מדומה (`SIMULATED`).
- [ ] `python main.py --live` מתחבר ל-OSRM API האמיתי ומדפיס שהמידע אמיתי (`LIVE`).
- [ ] `git status` נקי, אין קובץ `.env` במאגר, וכל ה-Commits של שלב 2 (כולל שלושת ה-Commits של TDD) מתועדים ב-`README.md`.