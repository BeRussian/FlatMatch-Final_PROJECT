# מדריך מקיף: מה ניצן וגיא עשו בחלק הראשון (שלב 1) 🛠️
> מסמך הסבר מעמיק, מפורט ומקצועי על כל מבני הנתונים, האיטרטורים, המחוללים ומנהלי ההקשר שנבנו בשלב 1.
> נכתב כדי שתשלוט בכל שורת קוד בפרויקט ב-100% לקראת הצגת הפרויקט והבחינה.

---

## 🧭 מפת אחריויות כללית בשלב 1
1. **אתה (ניק):** פיתוח ארכיטקטורת ה-OOP (חלק ב'), מודל הנתונים הבסיסי, מערכת האימותים והתכונות (Properties), ומחלקות המשתמשים והדירות (`Apartment`, `ApartmentSeeker`, `RoommateSeeker`, `Preferences`).
2. **ניצן כדורי (חלק ג' וחלק ה'):** מבני נתונים מתקדמים, תורים, ערימות, מילונים, פעולות על סטים וארגון החבילה (`flatmatch/processing.py`, ארגון החבילה וההרצה ב-`main.py`).
3. **גיא עפת (חלק ד'):** יעילות זיכרון, איטרטורים עצמאיים, גנרטורים, צינור עיבוד עצל (Lazy Pipeline), מנהלי הקשר עם Rollback ומאגר נתונים מבוסס קובץ (`flatmatch/iterators.py`, `flatmatch/context_managers.py`, `flatmatch/repository.py`, ו-`test_part_d.py`).

---

## 👨‍💻 חלק ג': מבני נתונים מתקדמים ועיבוד (ניצן כדורי)
הקוד המרכזי שכתב ניצן נמצא בקובץ: `flatmatch/processing.py`.

### 1. קבוצות ופעולות על סטים (Advanced Set Operations)
* **הצורך העסקי:** לכל דירה יש אוסף פינוקים (Amenities) שהיא מציעה (מזגן, מעלית, מרפסת, חניה), ולכל מחפש דירה יש אוסף פינוקים שהוא דורש.
* **הפונקציה שכתב ניצן:** `compare_amenities(desired_amenities: set, available_amenities: set) -> dict`
* **איך זה עובד טכנית?**
  ```python
  # בדיקת שייכות בסיבוכיות O(1)
  has_air_conditioner = "Air Conditioner" in available_amenities

  # חיתוך (Intersection - &): מה שנמצא בשתי הקבוצות
  matching = desired_amenities & available_amenities

  # הפרש (Difference - -): מה שהמחפש רצה אבל חסר בדירה
  missing = desired_amenities - available_amenities

  # איחוד (Union - |): כלל הפינוקים המשותפים והייחודיים
  all_combined = desired_amenities | available_amenities
  ```
* **למה דווקא Set?** בדיקת שייכות (`in`) ב-Set רצה בסיבוכיות ממוצעת של $O(1)$ לעומת $O(n)$ ברשימה (List). בנוסף, Set מונע כפילויות באופן מובנה.

---

### 2. תור FIFO (ראשון נכנס - ראשון יוצא) בעזרת `collections.deque`
* **הצורך העסקי:** כשיש חדר מבוקש בדירה ומגיעות פניות משותפים, כדי למנוע אפליה ולהבטיח שקיפות מוחלטת, יש לבדוק את הפניות בדיוק לפי סדר הגעתן (First-In, First-Out).
* **המחלקה שכתב ניצן:** `RoommateApplicationQueue`
* **למה `collections.deque` ולא רשימה רגילה (`list`)?**
  ברשימה רגילה בפייתון, פעולת `list.pop(0)` גוררת הזזה של כל איברי הרשימה מקום אחד שמאלה בזיכרון – פעולה כבדה של $O(n)$.
  ב-`deque` (רשימה מקושרת דו-כיוונית ב-C), שליפת האיבר הראשון (`popleft()`) והכנסה לסוף (`append()`) מתבצעות בסיבוכיות של **$O(1)$ קבוע**!
* **איך זה נראה בקוד?**
  ```python
  class RoommateApplicationQueue:
      def __init__(self):
          self._queue = deque()

      def enqueue_application(self, applicant_name, apartment_id, timestamp):
          self._queue.append((applicant_name, apartment_id, timestamp))  # O(1)

      def process_next_application(self):
          if not self._queue:
              return None
          return self._queue.popleft()  # O(1) מהיר ויעיל
  ```

---

### 3. תור עדיפויות (Priority Queue) בעזרת `heapq`
* **הצורך העסקי:** ישנם מקרים שבהם הדחיפות של המועמד גוברת על שעת הגעתו (למשל: מועמד שחייב לעבור מחר כי החוזה שלו הסתיים, לעומת מועמד שמחפש לעוד חודשיים).
* **המחלקה שכתב ניצן:** `UrgentCandidateQueue` ו-`PriorityCandidate`.
* **איך זה עובד טכנית?**
  * ניצן השתמש בערימת מינימום מובנית (Min-Heap) של ספריית `heapq`.
  * מוסכמת העדיפות: **מספר נמוך יותר = עדיפות גבוהה יותר** (עדיפות 1 דחופה יותר מעדיפות 3).
  * כדי לשבור שוויון במקרה של שני מועמדים עם אותה רמת עדיפות, הוא הוסיף מונה מספרי (`entry_id`) שפותר את השוויון לפי סדר ההגעה.
  * הפעולות `heappush` ו-`heappop` רצות בזמן מהיר ביותר של **$O(\log n)$**.

---

### 4. מילונים, קיבוץ וספירה (Grouping & Counting)
* **הצורך העסקי:** קיבוץ מועמדים לפי ערי יעד וספירת כמות המועמדים בכל אזור.
* **הפונקציות שכתב ניצן:**
  * `group_seekers_by_city(seekers)`: מילון שבו המפתח הוא שם העיר, והערך הוא רשימת המועמדים באותה עיר.
  * `count_seekers_by_city(seekers)`: מילון שסופר כמה מועמדים יש בכל עיר בעזרת `counts[city] = counts.get(city, 0) + 1`.
  * `add_user_to_lookup(user_dict, user_id, user_obj)`: מניעת כפילויות תעודות זהות או מספרי טלפון (זריקת `ValueError` אם המספר כבר קיים).

---

## 👨‍💻 חלק ד': איטרטורים, גנרטורים ומנהלי הקשר (גיא עפת)
הקוד שכתב גיא מפוצל לשלושה קבצים: `iterators.py`, `context_managers.py`, ו-`repository.py`.

### 1. איטרטור עצמאי (`SeekerIterator` ו-`SeekerCollection`)
* **הקובץ:** `flatmatch/iterators.py`
* **הצורך:** הבנה עמוקה של פרוטוקול האיטרציה בפייתון (כיצד לולאת `for` עובדת מתחת למכסה המנוע).
* **איך גיא מימש את זה?**
  * `SeekerCollection`: מחלקה המחזיקה את רשימת המועמדים. המתודה `__iter__()` שלה מייצרת אובייקט איטרטור חדש ועצמאי לחלוטין.
  * `SeekerIterator`: מחזיק מצביע (סמן / `cursor`) פנימי.
    * המתודה `__iter__()` מחזירה את האיטרטור עצמו (`return self`).
    * המתודה `__next__()` מחזירה את האיבר הבא ומקדמת את הסמן.
    * כשמגיעים לסוף הרשימה, היא זורקת חריגת **`StopIteration`** (שזה האות של לולאת `for` לעצור).
* **היתרון:** ניתן ליצור שני איטרטורים שונים על אותו האוסף בדיוק, וכל אחד מהם ירוץ בקצב שלו בלי להשפיע על השני!

---

### 2. מחוללים (Generators) וצינור עיבוד עצל (Lazy Pipeline)
* **הקובץ:** `flatmatch/iterators.py`
* **הצורך בביצועים ובזיכרון:**
  אם במערכת יש 100,000 דירות, אסור לייצר רשימות זמניות גדולות בזיכרון ה-RAM עבור כל סינון.
* **מה גיא בנה?**
  1. פונקציית Generator עם `yield`:
     ```python
     def stream_budget_candidates(seekers, max_budget_ceiling: float):
         for seeker in seekers:
             if seeker.max_budget <= max_budget_ceiling:
                 yield seeker  # מייצר מועמד אחד בכל פעם ומשהה את הפונקציה!
     ```
  2. צינור עיבוד עצל תלת-שלבי (`build_lazy_seeker_pipeline`):
     שרשור של 3 ביטויי מחולל (Generator Expressions) בזה אחר זה:
     * **שלב 1:** סינון לפי עיר מבוקשת.
     * **שלב 2:** סינון לפי רמת ניקיון מינימלית.
     * **שלב 3:** טרנספורמציה למחרוזת סיכום.
     **חשוב מאוד:** שום רשימה לא נוצרת בזיכרון! המועמדים "נשאבים" דרך הצינור בזה אחר זה רק כאשר הקוד הצרכן קורא ל-`next()` או רץ בלולאה.

---

### 3. מנהלי הקשר (Context Managers) עם Rollback אוטומטי
* **הקובץ:** `flatmatch/context_managers.py`
* **הצורך העסקי:** כשיש תהליך שמשריין דירה לבדיקה, אסור שהדירה תישאר "תקועה" בסטטוס שמור במקרה של תקלה.
* **המחלקה שכתב גיא:** `ApartmentHoldContext`
* **איך זה עובד? (תחביר ה-`with`):**
  ```python
  class ApartmentHoldContext:
      def __init__(self, apartment, applicant_name):
          self.apartment = apartment
          self.applicant_name = applicant_name
          self.previous_status = getattr(apartment, "status", "AVAILABLE")

      def __enter__(self):
          # כניסה לבלוק ה-with: נעילת הדירה
          self.apartment.status = "ON_HOLD"
          return self

      def __exit__(self, exc_type, exc_val, exc_tb):
          # יציאה מבלוק ה-with: בדיקה האם קרתה שגיאה
          if exc_type is not None:
              # הייתה שגיאה! מבצעים שחזור (Rollback) אוטומטי למצב המקורי
              self.apartment.status = self.previous_status
              print(f"Exception caught! Rolled back apartment status to {self.previous_status}")
              return False  # מעביר הלאה את השגיאה, לא בולע אותה
          
          return False
  ```
* בנוסף, גיא כתב את `SearchSessionContext` שמודד במדויק את זמן החיפוש של המשתמש בעזרת `time.perf_counter()`.

---

### 4. מאגר הנתונים השורתי (`FlatMatchRepository`)
* **הקובץ:** `flatmatch/repository.py`
* **הצורך:** קריאת נתונים מקובץ JSONL (קובץ שבו כל שורה היא אובייקט JSON נפרד).
* **מה גיא עשה?**
  * קריאה שורה-שורה (Streaming) באמצעות מחולל `yield`, כך שניתן לקרוא קבצים בגודל גיגה-בייטים מבלי לחרוג מזיכרון ה-RAM.
  * בניית אינדקס מילוני מקביל לפי מספרי טלפון, המאפשר שליפת משתמש ב-$O(1)$ מהיר בעזרת `repo.get_by_phone(phone)`.
* **בדיקות היחידה של גיא:** הקובץ `test_part_d.py` כולל 7 בדיקות ייעודיות שמוודאות את כל הלוגיקה של חלק ד'.

---
*מסמך זה מאגד את כל תרומתם של ניצן וגיא לשלב 1.*
