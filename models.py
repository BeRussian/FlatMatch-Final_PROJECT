from abc import ABC, abstractmethod


class Preferences:
    # הגדרת כל המשתנים להעדפות המשתמשים
    # לכל העדפה מוגדר ערך ברירת מחדל

    def __init__(
        self,
        cleanliness: int = 3,  # 1-5 מספרים יותר גבוהים = יותר נקי
        allows_pets: bool = False,  # האם מותר חיות מחמד
        is_smoker: bool = False,  # האם מעשן
        sleep_schedule: str = "flexible",  # flexible, morning_person, night_owl
        kashrut_level: str = "hiloni",  # hiloni, low, medium, high
        shabbat_observant: bool = False,  # שומר שבת
    ):
        if type(cleanliness) != int or not (1 <= cleanliness <= 5):
            raise ValueError("Cleanliness must be between 1 and 5")
        self._cleanliness = cleanliness

        if type(allows_pets) != bool:
            raise ValueError("allow_pets must be True/False")
        self._allows_pets = allows_pets

        if type(is_smoker) != bool:
            raise ValueError("is_smoker must be True/False")
        self._is_smoker = is_smoker

        if type(sleep_schedule) != str:
            raise ValueError("sleep_schedule must be str")
        if sleep_schedule != "flexible" and sleep_schedule != "flexiable" and sleep_schedule != "morning_person" and sleep_schedule != "night_owl":
            raise ValueError("sleep_schedule must be [flexible / morning_person / night_owl]")
        self._sleep_schedule = sleep_schedule

        if type(kashrut_level) != str:
            raise ValueError("kashrut_level must be str")
        if kashrut_level != "low" and kashrut_level != "medium" and kashrut_level != "high" and kashrut_level != "hiloni":
            raise ValueError("kashrut_level must be [hiloni / low / medium / high]")
        self._kashrut_level = kashrut_level

        if type(shabbat_observant) != bool:
            raise ValueError("shabbat_observant must be True/False")
        self._shabbat_observant = shabbat_observant

    @property
    def cleanliness(self):
        return self._cleanliness

    @cleanliness.setter
    def cleanliness(self, value: int):
        if type(value) != int or not (1 <= value <= 5):
            raise ValueError("Cleanliness must be between 1 and 5")
        self._cleanliness = value

    @property
    def allows_pets(self):
        return self._allows_pets

    @allows_pets.setter
    def allows_pets(self, value: bool):
        if type(value) != bool:
            raise ValueError("allow_pets must be True/False")
        self._allows_pets = value

    @property
    def is_smoker(self):
        return self._is_smoker

    @is_smoker.setter
    def is_smoker(self, value: bool):
        if type(value) != bool:
            raise ValueError("is_smoker must be True/False")
        self._is_smoker = value

    @property
    def sleep_schedule(self):
        return self._sleep_schedule

    @sleep_schedule.setter
    def sleep_schedule(self, value: str):
        if type(value) != str:
            raise ValueError("sleep_schedule must be str")
        if value != "flexible" and value != "flexiable" and value != "morning_person" and value != "night_owl":
            raise ValueError("sleep_schedule must be [flexible / morning_person / night_owl]")
        self._sleep_schedule = value

    @property
    def kashrut_level(self):
        return self._kashrut_level

    @kashrut_level.setter
    def kashrut_level(self, value: str):
        if type(value) != str:
            raise ValueError("kashrut_level must be str")
        if value != "low" and value != "medium" and value != "high" and value != "hiloni":
            raise ValueError("kashrut_level must be [hiloni / low / medium / high]")
        self._kashrut_level = value

    @property
    def shabbat_observant(self):
        return self._shabbat_observant

    @shabbat_observant.setter
    def shabbat_observant(self, value: bool):
        if type(value) != bool:
            raise ValueError("shabbat_observant must be True/False")
        self._shabbat_observant = value

    # פונקציה שמשווה משתמשים ובודקת האם יש פסילה שלא מאפשר לגור ביחד
    def has_conflict(self, other):
        if self.is_smoker != other.is_smoker:
            return True
        if self.allows_pets != other.allows_pets:
            return True
        return False

    def __str__(self) -> str:
        return (
            f"Preferences(cleanliness={self.cleanliness}, allows_pets={self.allows_pets}, "
            f"is_smoker={self.is_smoker}, sleep_schedule='{self.sleep_schedule}', "
            f"kashrut='{self.kashrut_level}', "
            f"shabbat='{self.shabbat_observant}')"
        )


class Apartment:
    # רשימת ערים נתמכות באנגלית בלבד
    SUPPORTED_CITIES = {
        "Tel Aviv", "Jerusalem", "Haifa", "Beer Sheva", "Ramat Gan",
        "Givatayim", "Herzliya", "Rishon LeZion", "Petah Tikva", "Holon",
        "Bat Yam", "Netanya", "Kfar Saba", "Ra'anana", "Ashdod", "Ashkelon", "Modi'in"
    }

    def __init__(self, city: str, rent: float, rooms: int = 1, amenities: set = None):
        if not self.is_valid_city(city):
            raise ValueError(f"City '{city}' is invalid or not in supported cities")
        self._city = city.strip()

        if not isinstance(rent, (int, float)) or rent <= 0:
            raise ValueError("Rent must be a positive number")
        self._rent = float(rent)

        if type(rooms) != int or rooms <= 0:
            raise ValueError("Rooms must be a positive integer")
        self._rooms = rooms

        self._amenities = set()
        if amenities != None:
            if not isinstance(amenities, (set, list, tuple)):
                raise ValueError("amenities must be a set, list, or tuple")
            for item in amenities:
                self.add_amenity(item)

    @staticmethod
    def is_valid_city(city: str) -> bool:
        if not isinstance(city, str) or not city.strip():
            return False
        clean = city.strip().lower()
        supported_lower = {c.lower() for c in Apartment.SUPPORTED_CITIES}
        return clean in supported_lower

    @property
    def city(self) -> str:
        return self._city

    @city.setter
    def city(self, value: str):
        if not self.is_valid_city(value):
            raise ValueError(f"City '{value}' is invalid or not in supported cities")
        self._city = value.strip()

    @property
    def rent(self) -> float:
        return self._rent

    @rent.setter
    def rent(self, value: float):
        if not isinstance(value, (int, float)) or value <= 0:
            raise ValueError("Rent must be a positive number")
        self._rent = float(value)

    @property
    def rooms(self) -> int:
        return self._rooms

    @rooms.setter
    def rooms(self, value: int):
        if type(value) != int or value <= 0:
            raise ValueError("Rooms must be a positive integer")
        self._rooms = value

    @property
    def rent_per_room(self) -> float:
        # Computed property: מחשב דינמית שכר דירה ממוצע לחדר
        return round(self._rent / self._rooms, 2)

    @property
    def amenities(self) -> set:
        return self._amenities.copy()

    def add_amenity(self, amenity: str):
        if not isinstance(amenity, str) or not amenity.strip():
            raise ValueError("Amenity must be a non-empty str")
        self._amenities.add(amenity.strip())

    def remove_amenity(self, amenity: str):
        if not isinstance(amenity, str):
            raise ValueError("Amenity must be a str")
        self._amenities.discard(amenity.strip())

    def has_amenity(self, amenity: str) -> bool:
        if not isinstance(amenity, str):
            return False
        return amenity.strip() in self._amenities

    def __str__(self) -> str:
        amenities_str = ", ".join(self._amenities) if len(self._amenities) > 0 else "None"
        return f"Apartment(city='{self._city}', rent={self._rent}, rooms={self._rooms}, avg_per_room={self.rent_per_room}, amenities=[{amenities_str}])"


class User(ABC):
    def __init__(self, name: str, age: int, phone: str, preferences_OBJ: Preferences = None):
        if type(name) != str or not name.strip():
            raise ValueError("name must be a non-empty str")
        self._name = name.strip()

        if type(age) != int or not (18 <= age <= 120):
            raise ValueError("age must be an integer between 18 and 120")
        self._age = age

        if type(phone) != str or not phone.strip():
            raise ValueError("phone must be a non-empty str")
        self._phone = phone.strip()

        if preferences_OBJ != None and not isinstance(preferences_OBJ, Preferences):
            raise ValueError("preferences_OBJ must be an instance of Preferences")
        self._preferences = preferences_OBJ if preferences_OBJ != None else Preferences()

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value: str):
        if type(value) != str or not value.strip():
            raise ValueError("name must be a non-empty str")
        self._name = value.strip()

    @property
    def age(self):
        return self._age

    @age.setter
    def age(self, value: int):
        if type(value) != int or not (18 <= value <= 120):
            raise ValueError("age must be an integer between 18 and 120")
        self._age = value

    @property
    def phone(self):
        return self._phone

    @phone.setter
    def phone(self, value: str):
        if type(value) != str or not value.strip():
            raise ValueError("phone must be a non-empty str")
        self._phone = value.strip()

    @property
    def preferences(self):
        return self._preferences

    @preferences.setter
    def preferences(self, value: Preferences):
        if not isinstance(value, Preferences):
            raise ValueError("preferences must be an instance of Preferences")
        self._preferences = value

    def __str__(self):
        return f"User: {self._name}, Age: {self._age}, Phone: {self._phone}"

    @abstractmethod
    def get_role_summary(self):
        pass

    @abstractmethod
    def evaluate_dealbreakers(self, other):
        pass


class ApartmentSeeker(User):
    def __init__(
        self,
        name: str,
        age: int,
        phone: str,
        max_budget: float,
        preferred_cities: list,
        preferences_OBJ: Preferences = None
    ):
        super().__init__(name=name, age=age, phone=phone, preferences_OBJ=preferences_OBJ)

        if not isinstance(max_budget, (int, float)) or max_budget <= 0:
            raise ValueError("max_budget must be a positive number")
        self._max_budget = float(max_budget)

        if not isinstance(preferred_cities, list) or len(preferred_cities) == 0:
            raise ValueError("preferred_cities must be a non-empty list of cities")
        for city in preferred_cities:
            if not isinstance(city, str) or not city.strip():
                raise ValueError("Each city in preferred_cities must be a non-empty str")
        self._preferred_cities = [c.strip() for c in preferred_cities]

    @property
    def max_budget(self) -> float:
        return self._max_budget

    @max_budget.setter
    def max_budget(self, value: float):
        if not isinstance(value, (int, float)) or value <= 0:
            raise ValueError("max_budget must be a positive number")
        self._max_budget = float(value)

    @property
    def preferred_cities(self) -> list:
        return self._preferred_cities.copy()

    @preferred_cities.setter
    def preferred_cities(self, value: list):
        if not isinstance(value, list) or len(value) == 0:
            raise ValueError("preferred_cities must be a non-empty list of cities")
        for city in value:
            if not isinstance(city, str) or not city.strip():
                raise ValueError("Each city in preferred_cities must be a non-empty str")
        self._preferred_cities = [c.strip() for c in value]

    @classmethod
    def from_dict(cls, data: dict):
        if not isinstance(data, dict):
            raise TypeError("data must be a dict")

        pref_data = data.get("preferences")
        if isinstance(pref_data, dict):
            pref_obj = Preferences(**pref_data)
        elif isinstance(pref_data, Preferences):
            pref_obj = pref_data
        else:
            pref_obj = None

        return cls(
            name=data["name"],
            age=data["age"],
            phone=data["phone"],
            max_budget=data["max_budget"],
            preferred_cities=data["preferred_cities"],
            preferences_OBJ=pref_obj
        )

    def __lt__(self, other):
        if not isinstance(other, ApartmentSeeker):
            return NotImplemented
        return self._max_budget < other._max_budget

    def get_role_summary(self) -> str:
        cities_str = ", ".join(self._preferred_cities)
        return f"Apartment Seeker: {self.name}, Age: {self.age}, Max Budget: {self._max_budget} NIS, Preferred Cities: [{cities_str}]"

    def evaluate_dealbreakers(self, other) -> bool:
        # בודק אם השכ"ד חורג או שהעיר לא ברשימת הערים המבוקשות
        if isinstance(other, RoommateSeeker):
            apt = other.apartment
            if apt.rent > self._max_budget:
                return True
            cities_lower = [c.lower() for c in self._preferred_cities]
            if apt.city.strip().lower() not in cities_lower:
                return True
            if self.preferences.has_conflict(other.preferences):
                return True
            return False

        if isinstance(other, Apartment):
            if other.rent > self._max_budget:
                return True
            cities_lower = [c.lower() for c in self._preferred_cities]
            if other.city.strip().lower() not in cities_lower:
                return True
            return False

        return False


class RoommateSeeker(User):
    def __init__(
        self,
        name: str,
        age: int,
        phone: str,
        apartment: Apartment,
        preferences_OBJ: Preferences = None
    ):
        super().__init__(name=name, age=age, phone=phone, preferences_OBJ=preferences_OBJ)

        if not isinstance(apartment, Apartment):
            raise ValueError("apartment must be an instance of Apartment")
        self._apartment = apartment

    @property
    def apartment(self) -> Apartment:
        return self._apartment

    @apartment.setter
    def apartment(self, value: Apartment):
        if not isinstance(value, Apartment):
            raise ValueError("apartment must be an instance of Apartment")
        self._apartment = value

    def get_role_summary(self) -> str:
        return f"Roommate Seeker: {self.name}, Age: {self.age}, Offering: {self._apartment}"

    def evaluate_dealbreakers(self, other) -> bool:
        # בודקת אם המועמד עומד בשכ"ד והאם אין סתירת עישון/חיות
        if isinstance(other, ApartmentSeeker):
            if other.max_budget < self._apartment.rent:
                return True
            if self.preferences.has_conflict(other.preferences):
                return True
            return False

        if hasattr(other, "preferences") and self.preferences.has_conflict(other.preferences):
            return True

        return False


# ==============================================================================
# יצירת מופעים לדוגמה: 5 מועמדים מכל סוג (Sample Data)
# ==============================================================================

def create_sample_data():
    # 5 מחפשי דירה (Apartment Seekers)
    seekers = [
        ApartmentSeeker(
            name="Alice Cohen",
            age=24,
            phone="050-1112233",
            max_budget=3200,
            preferred_cities=["Tel Aviv", "Ramat Gan"],
            preferences_OBJ=Preferences(cleanliness=4, allows_pets=False, is_smoker=False, sleep_schedule="morning_person", kashrut_level="hiloni", shabbat_observant=False)
        ),
        ApartmentSeeker(
            name="Ben Levi",
            age=27,
            phone="052-2223344",
            max_budget=4200,
            preferred_cities=["Tel Aviv", "Givatayim", "Ramat Gan"],
            preferences_OBJ=Preferences(cleanliness=5, allows_pets=True, is_smoker=False, sleep_schedule="flexible", kashrut_level="low", shabbat_observant=False)
        ),
        ApartmentSeeker(
            name="Dana Mizrahi",
            age=23,
            phone="054-3334455",
            max_budget=2800,
            preferred_cities=["Jerusalem"],
            preferences_OBJ=Preferences(cleanliness=3, allows_pets=False, is_smoker=False, sleep_schedule="night_owl", kashrut_level="high", shabbat_observant=True)
        ),
        ApartmentSeeker(
            name="Eitan Sharon",
            age=29,
            phone="053-4445566",
            max_budget=3800,
            preferred_cities=["Haifa", "Herzliya"],
            preferences_OBJ=Preferences(cleanliness=4, allows_pets=True, is_smoker=True, sleep_schedule="flexible", kashrut_level="hiloni", shabbat_observant=False)
        ),
        ApartmentSeeker(
            name="Maya Golan",
            age=25,
            phone="058-5556677",
            max_budget=3500,
            preferred_cities=["Beer Sheva"],
            preferences_OBJ=Preferences(cleanliness=4, allows_pets=False, is_smoker=False, sleep_schedule="morning_person", kashrut_level="medium", shabbat_observant=False)
        )
    ]

    # 5 מציעי שותפות בדירה (Roommate Seekers)
    owners = [
        RoommateSeeker(
            name="Yossi Avraham",
            age=26,
            phone="050-6667788",
            apartment=Apartment(city="Tel Aviv", rent=3500, rooms=2, amenities={"Air Conditioner", "Balcony", "Elevator"}),
            preferences_OBJ=Preferences(cleanliness=4, allows_pets=False, is_smoker=False, sleep_schedule="flexible", kashrut_level="hiloni", shabbat_observant=False)
        ),
        RoommateSeeker(
            name="Noa Peretz",
            age=28,
            phone="052-7778899",
            apartment=Apartment(city="Ramat Gan", rent=3000, rooms=3, amenities={"Air Conditioner", "Mamad"}),
            preferences_OBJ=Preferences(cleanliness=5, allows_pets=True, is_smoker=False, sleep_schedule="morning_person", kashrut_level="low", shabbat_observant=False)
        ),
        RoommateSeeker(
            name="Itamar Friedman",
            age=25,
            phone="054-8889900",
            apartment=Apartment(city="Jerusalem", rent=2600, rooms=2, amenities={"Balcony"}),
            preferences_OBJ=Preferences(cleanliness=3, allows_pets=False, is_smoker=False, sleep_schedule="night_owl", kashrut_level="high", shabbat_observant=True)
        ),
        RoommateSeeker(
            name="Tomer Katz",
            age=30,
            phone="053-9990011",
            apartment=Apartment(city="Haifa", rent=3700, rooms=3, amenities={"Air Conditioner", "Balcony", "Mamad", "Elevator"}),
            preferences_OBJ=Preferences(cleanliness=4, allows_pets=True, is_smoker=True, sleep_schedule="flexible", kashrut_level="hiloni", shabbat_observant=False)
        ),
        RoommateSeeker(
            name="Shira Bar",
            age=24,
            phone="058-0001122",
            apartment=Apartment(city="Beer Sheva", rent=2400, rooms=2, amenities={"Air Conditioner"}),
            preferences_OBJ=Preferences(cleanliness=4, allows_pets=False, is_smoker=False, sleep_schedule="morning_person", kashrut_level="medium", shabbat_observant=False)
        )
    ]

    return seekers, owners


sample_apartment_seekers, sample_roommate_seekers = create_sample_data()


if __name__ == "__main__":
    print("=== Models and Sample Instances Verification ===")
    seekers, owners = sample_apartment_seekers, sample_roommate_seekers
    
    print(f"Successfully created {len(seekers)} Apartment Seekers and {len(owners)} Roommate Seekers.")
    print("\n--- Sample Apartment Seeker ---")
    print(seekers[0].get_role_summary())
    
    print("\n--- Sample Roommate Seeker ---")
    print(owners[0].get_role_summary())
    
    print("\n--- Dealbreaker Filtering Verification ---")
    # Yossi דורש 3500 שכ"ד, התקציב של Alice הוא 3200 -> אמור להיות Dealbreaker
    conflict_alice_yossi = seekers[0].evaluate_dealbreakers(owners[0])
    print(f"Dealbreaker between Alice and Yossi (Budget 3200 vs Rent 3500): {conflict_alice_yossi}")
    assert conflict_alice_yossi == True

    # Ben Levi תקציב 4200, Noa Peretz שכ"ד 3000, שניהם מאשרים חיות ואף אחד לא מעשן -> אין Dealbreaker!
    conflict_ben_noa = seekers[1].evaluate_dealbreakers(owners[1])
    print(f"Dealbreaker between Ben and Noa (Full Match): {conflict_ben_noa}")
    assert conflict_ben_noa == False

    print("\nAll logic tests passed successfully!")
