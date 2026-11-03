# 🤖 תיעוד שימוש אחראי ב-AI (`AI_USAGE.md`)

מסמך זה מתעד את השימוש בכלי בינה מלאכותית (AI) במסגרת שלב 1 בפרויקט **FlatMatch**, בהתאם להנחיות הרשמיות של הקורס.

---

## 🛠️ 1. כלי ה-AI ששימשו בפרויקט
- **שם הכלי המרכזי:** Claude 3.5 Sonnet / Google Gemini
- **סביבת עבודה:** Antigravity IDE (Pair Programming Agent)
- **מטרה עיקרית:** יצירת נתוני התחלה סינתטיים (`data/sample_data.jsonl`), סיעור מוחות לאפיון ותרחישי קצה לבדיקות.

---

## 📝 2. הפנייה (Prompt) ליצירת נתוני ההתחלה
להלן הפנייה הסופית והמדויקת ששימשה ליצירת 20 הרשומות הסינתטיות בקובץ `data/sample_data.jsonl`:

```text
Please generate 20 synthetic, realistic JSON records for a Python shared-apartment matching system called FlatMatch.

Formatting Requirements:
1. Output format: JSON Lines (JSONL) - exactly one valid JSON object per line, without markdown fences or empty lines.
2. Distribution: Exactly 15 ApartmentSeeker records and 5 RoommateSeeker records.
3. Privacy: Do NOT use real personal information, real phone numbers, or existing people. Use realistic Israeli mock names and sequential dummy phones (e.g., "050-1000001" to "050-1000015" for seekers, and "050-2000001" to "050-2000005" for owners).

Schema & Validation Rules:
1. ApartmentSeeker records:
   - "type": "apartment_seeker"
   - "name": non-empty string
   - "age": integer between 20 and 35
   - "phone": unique string
   - "max_budget": positive float (2500.0 - 4500.0)
   - "preferred_cities": non-empty list of supported Israeli cities in English:
     ["Tel Aviv", "Ramat Gan", "Givatayim", "Jerusalem", "Haifa", "Beer Sheva", "Herzliya", "Netanya", "Kfar Saba", "Petah Tikva", "Holon", "Rishon LeZion"]
   - "preferences": dictionary containing:
     * "cleanliness": integer from 1 to 5
     * "allows_pets": boolean
     * "is_smoker": boolean
     * "sleep_schedule": exactly one of ["flexible", "morning_person", "night_owl"]
     * "kashrut_level": exactly one of ["hiloni", "low", "medium", "high"]
     * "shabbat_observant": boolean

2. RoommateSeeker records:
   - "type": "roommate_seeker"
   - "name": non-empty string
   - "age": integer between 24 and 35
   - "phone": unique string
   - "apartment": dictionary containing:
     * "city": one of the supported cities listed above
     * "rent": positive float (2400.0 - 3800.0)
     * "rooms": integer between 1 and 4
     * "amenities": list of amenity strings (e.g., ["Air Conditioner", "Balcony", "Elevator", "Parking", "Mamad"])
   - "preferences": same structure as above.
```

---

## 🏗️ 3. מבנה הרשומות שנתבקש (Schema)

| ישות | שדה | טיפוס | אילוצים / ערכים מותרים |
| :--- | :--- | :--- | :--- |
| **משותף לכולם** | `type` | `str` | `"apartment_seeker"` או `"roommate_seeker"` |
| | `name` | `str` | שם מלא תקין באנגלית, ללא מחרוזת ריקה |
| | `age` | `int` | טווח תקין: $18 \le \text{age} \le 120$ |
| | `phone` | `str` | מזהה ייחודי חד-חד-ערכי (פורמט `050-XXXXXXX`) |
| **העדפות (`preferences`)** | `cleanliness` | `int` | $1 \le \text{value} \le 5$ בלבד |
| | `allows_pets` | `bool` | `True` / `False` |
| | `is_smoker` | `bool` | `True` / `False` |
| | `sleep_schedule` | `str` | ערכים מוגדרים מראש: `"flexible"`, `"morning_person"`, `"night_owl"` |
| | `kashrut_level` | `str` | ערכים מוגדרים מראש: `"hiloni"`, `"low"`, `"medium"`, `"high"` |
| | `shabbat_observant` | `bool` | `True` / `False` |
| **מחפש דירה (`ApartmentSeeker`)** | `max_budget` | `float` | מספר חיובי ($> 0$) |
| | `preferred_cities` | `list[str]` | רשימה שאינה ריקה של ערים נתמכות |
| **מציע שותפות (`RoommateSeeker`)**| `apartment.city` | `str` | עיר מתוך רשימת `Apartment.SUPPORTED_CITIES` |
| | `apartment.rent` | `float` | שכר דירה חודשי חיובי ($> 0$) |
| | `apartment.rooms` | `int` | מספר חדרים חיובי ($> 0$) |
| | `apartment.amenities`| `list[str]` | רשימת מתקנים (מומרת ל-`set` באובייקט) |

---

## 🔍 4. בעיות שנמצאו בנתונים, תיקונים ואופן האימות

במהלך תהליך הבדיקה והטעינה של הנתונים הסינתטיים אותרו ותוקנו הנקודות הבאות:

1. **אימות חד-חד-ערכיות של מזהי טלפון (Phone Uniqueness):**
   - *בעיה אפשרית:* חשש לשכפול מזהה שהיה גורם לקריסה ב-`FlatMatchRepository` בעת איתור לפי מפתח.
   - *תיקון ואימות:* נבחנו כל 20 הרשומות, ונוצר טווח מזהים עוקב ונפרד (`050-1000001..015` למחפשים, ו-`050-2000001..005` לבעלי דירות). בוצעה בדיקה שכל מספרי הטלפון ייחודיים לחלוטין.
2. **אימות שמות ערים נתמכות:**
   - *בעיה אפשרית:* כלי AI עשויים לייצר שמות ערים בעברית או ערים שאינן נתמכות על ידי המחלקה `Apartment`, דבר שהיה גורר זריקת `ValueError`.
   - *תיקון ואימות:* כל עיר ב-`preferred_cities` וב-`apartment.city` אומתה מול `Apartment.SUPPORTED_CITIES` באנגלית.
3. **שמירה על פורמט שורה אחת (JSONL):**
   - *תיקון:* הוסרו שורות ריקות ורווחים מיותרים בסוף הקובץ, וכל אובייקט JSON נשמר בשורה בודדת ועצמאית הניתנת לקריאה על ידי ה-file iterator.
4. **אימות טעינה והמרה לאובייקטים:**
   - הקובץ נטען במלואו באמצעות `stream_users_from_jsonl` ו-`FlatMatchRepository(data_path)`.
   - נבדק שנפרסו בהצלחה 15 מופעי `ApartmentSeeker` ו-5 מופעי `RoommateSeeker` ללא שגיאות טיפוס.

---

## 💡 5. שימושי AI נוספים בפרויקט
- **תרשימי Mermaid ב-README.md:** יצירת תרשים מחלקות (Class Diagram) הממחיש באופן גרפי את ההורשה, ההרכבה והקשרים בין הישויות.
- **ניסוח מקרי קצה לבדיקות:** סיוע בהגדרת תרחישי שגיאה מבוקרים ב-Context Managers (כגון שגיאת חיבור יזומה שאינה נבלעת ב-`__exit__`).

---

## ✍️ 6. הצהרת הבנה ואחריות אישית
- כל שורת קוד בפרויקט, מבני הנתונים, ה-Iterators, ה-Generators וה-Context Managers נכתבו, נבדקו והובנו במלואם.
- נשמרה שליטה מלאה על הלוגיקה העסקית, ההחלטות הארכיטקטוניות ותאימות הקוד לכללי הקורס (כגון אי-שימוש באופרטור `is` להשוואת ערכים ושימוש אך ורק ב-Standard Library ללא ספריות חיצוניות).
- אנו מסוגלים להסביר כל חלק ומחלקה בפרויקט במסגרת ההגנה והבדיקה.

---

## 🤖 7. תיעוד שימוש אחראי ב-AI לשלב 2 (Stage 2 Architecture, API & Concurrency)

בהתאם לסעיף 7.3 בסילבוס, להלן תיעוד מפורט של העבודה עם כלי AI במסגרת שלב 2:

### 7.1 תוכניות ובדיקות שנכתבו לפני יצירת הקוד
לפני כתיבת שורת קוד אחת של המימוש, הוגדרה תוכנית עבודה מפורטת וסוויטת הבדיקות נכתבה מראש (Test-First Approach):
- **תכנון הצינור:** שלבי הצינור תוכננו מראש: נרמול כתובות מקומי -> המרה לקואורדינטות ב-Nominatim -> חישוב מסלול נסיעה ב-OSRM API -> אינטגרציה מול תבניות Strategy, Factory, Observer -> סנכרון תת-המערכת.
- **הגדרת מקרי הבדיקה ב-`tests/test_api_client.py` לפני המימוש:**
  1. נרמול קיצורים ישראליים נפוצים ללא קריסה על כתובות חופשיות.
  2. פענוח תקין של מענה JSON והמרתו ל-`CommuteMetrics`.
  3. הבחנה מוחלטת בין 4 סוגי חריגות (`APIConnectionError`, `APIHTTPError`, `APIResponseFormatError`, `APIDataValidationError`).
  4. מנגנון Retry של 3 ניסיונות בדיוק במקרה של Timeout / ConnectionError, והפסקה מיידית ללא Retry במקרה של שגיאת HTTP או נתונים פגומים.
  5. סנכרון מקבילי מוגן באמצעות Lock ומניעת רישום יתר.

### 7.2 שתי תוצאות צפויות שהוגדרו מראש (כולל מקרה כשל של השירות החיצוני)
1. **תוצאה צפויה 1 (מקרה הצלחה – ניתוב תקין):**
   - **קלט:** קואורדינטות מקור בדיזנגוף סנטר `(34.7743, 32.0754)` ויעד בקריה האקדמית אונו `(34.8624, 32.0617)`.
   - **תוצאה צפויה שהוגדרה מראש:** מתקבל אובייקט `CommuteMetrics` שבו `distance_km == 12.5`, `duration_minutes == 22.0`, והשדה `is_verified == True`.
2. **תוצאה צפויה 2 (מקרה כשל של השירות החיצוני):**
   - **קלט:** כשל תקשורת יזום (Simulated Timeout / ConnectionError) של ה-API.
   - **תוצאה צפויה שהוגדרה מראש:** מתבצעים בדיוק 3 ניסיונות פנייה (`assert mock_get.call_count == 3`), לאחריהם נזרקת החריגה המובחנת `APIConnectionError`. בשכבת השירות `FlatMatchService`, הכשל נתפס בצורה מבוקרת (Graceful Fallback) ומחזיר אובייקט גיבוי עם `is_verified == False`, הסטטוס מסומן כ-`PENDING_MANUAL_VERIFICATION`, והמערכת אינה קורסת.

### 7.3 הפעלת הבדיקות הקיימות כדי לוודא שאינן נפגעות
לפני כל שינוי ולאחר כל שילוב של רכיב חדש בשלב 2, הורצה סוויטת הבדיקות המקורית של שלב 1:
- `python test_part_d.py` (7 בדיקות מקוריות של Iterators, Generators ו-Context Managers).
- `pytest tests/test_stage1.py` (12 בדיקות התנהגויות שלב 1, מבני נתונים, שוויון ופולימורפיזם).
- **תוצאה:** 100% מהבדיקות הקיימות המשיכו לעבור בהצלחה מלאה (Zero Regression), תוך שמירה על ממשקי הקריאה הוותיקים.

### 7.4 ללא שינוי בדיעבד של התוצאות הצפויות כדי להתאים לפלט שגוי
**עיקרון מחמיר זה נשמר ללא חריגות:**
כאשר בדיקה נכשלה במהלך הפיתוח, לעולם לא שונו ערכי התוצאה הצפויה בבדיקה כדי להתאים לתוצאה השגויה של הקוד. במקום זאת, נותחה סיבת השורש בקוד המימוש (כגון שגיאת חישוב במדרגות התקציב או סדר הטיפול בחריגות) והקוד תוקן עד שהפיק את התוצאה העסקית הנכונה שהוגדרה מראש.

### 7.5 סיכום הצעות ה-AI, מה נבדק, ומה תוקן או שונה בעקבות הבדיקה
במהלך העבודה הוצעו על ידי מודל ה-AI מספר הצעות שאינן מתאימות לדרישות הקורס ונפסלו / תוקנו אנושית:
1. **הצעת AI:** שימוש ב-`time.sleep()` לצורך השהיות בין ניסיונות חוזרים (Retry) ובסעיף האסינכרוני.
   - **בדיקה ותיקון אנושי:** נבדק ונפסל! `time.sleep()` חוסם את ה-Event Loop של `asyncio` ומאט את הבדיקות האוטומטיות. תוקן כך שבקוד האסינכרוני נעשה שימוש בלעדי ב-`await asyncio.sleep()`, ובמחלקת ה-API הוטמעה הזרקת תלות (`sleep_func`), המאפשרת לבדיקות ה-Retry לרוץ ב-0 שניות ללא המתנה אמיתית.
2. **הצעת AI:** ביצוע Retry אוטומטי גם בעת קבלת קודי שגיאה 404/500 או JSON משובש.
   - **בדיקה ותיקון אנושי:** נבדק ותוקן! לפי סעיף 2.2 בסילבוס, חל איסור לנסות שוב בעקבות נתונים לא תקינים או שגיאות HTTP. הקוד תוקן כך שרק `Timeout` ו-`ConnectionError` זוכים ל-Retry (עד 3 פעמים), ושאר השגיאות נזרקות מיד כחריגות מובחנות.
3. **הצעת AI:** שימוש ב-Google Maps Distance Matrix API הדורש מפתחות סודיים בתשלום.
   - **בדיקה ותיקון אנושי:** נפסל לטובת ארכיטקטורת Zero-Key ציבורית המבוססת על OSRM ו-Nominatim, ללא צורך במפתחות סודיים, ללא סכנת חשיפת סודות ב-Git, ועם תמיכה מובנית ב-100% ריצה מקומית ואופליין.

### 7.6 הצהרת הבנה ואחריות אישית
כל שורת קוד, בדיקת pytest ורכיב ארכיטקטוני שנבנו בפרויקט FlatMatch נבדקו, הורצו והובנו במלואם. הצוות שולט לחלוטין בכל מנגנון סנכרון, מקביליות ואינטגרציית API, וערוך להסביר ולהגן עליהם במעמד ההגנה.
