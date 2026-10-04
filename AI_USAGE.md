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
