# 🏢 Project Proposal: FlatMatch

> **FlatMatch** – A smart apartment and roommate matching system (a "Tinder for Roommates") that filters, ranks, and suggests potential candidates based on personal preferences, lifestyle habits, and budget constraints.

---

## 🎯 1. Business Need and Problem Solved

Searching for roommates is often a frustrating process conducted through messy Facebook groups, requiring exhaustive manual filtering. The problem escalates when "blind matches" occur, leading to friction, conflicts, and prematurely broken leases due to lifestyle incompatibilities (e.g., cleanliness, sleeping habits, smoking). 

**The Solution:** The system transforms this process into a data-driven, precise, and efficient experience.

## 👥 2. Key Users and Roles

- **Apartment Seeker:** A user looking to join an existing shared apartment. They input their desired geographical area, budget, and lifestyle preferences.
- **Roommate Seeker:** A user who holds a lease for an apartment with an available room. They input the property details, rent, and their expectations for an incoming roommate.

## ⚙️ 3. Core Business Process

- **Trigger:** A user logs into the system and initiates a "Swipe Session" (search mode).
- **Process Flow:** The system activates a lazy data pipeline that fetches opposing profiles (e.g., displaying available rooms to an Apartment Seeker). It filters out profiles that violate hard constraints ("deal-breakers"), calculates a Match Score for the remaining candidates, and serves them sequentially based on priority. The user then accepts (Swipe Right) or rejects (Swipe Left) each suggestion.
- **Result:** When both parties mutually accept each other, a "Match" is created, granting them access to each other's contact information.

## 📊 4. Data Flow

- **Input:** Personal user data, hard constraints (price range, pet policies), and soft preferences (cleanliness level, social habits).
- **Updates:** Users dynamically update their preferences and log their responses (likes/dislikes) to suggested profiles.
- **Output:** A dynamically sorted queue of recommended candidates and a list of successful mutual matches for further communication.

## 💡 5. Expected Business Value

Significant reduction in time spent reviewing irrelevant candidates, prevention of financial loss and emotional distress caused by broken rental agreements due to personality clashes, and overall optimization of the shared-rental market experience.

## 🏗️ 6. Core Entities and Relationships

- **User:** An abstract/base entity containing foundational personal details and shared logic.
- **ApartmentSeeker / RoommateSeeker:** Child entities inheriting from `User`, polymorphically implementing distinct ranking and matching logic.
- **Apartment:** An entity managed by a RoommateSeeker (via Composition), encapsulating the physical property details (e.g., location, monthly rent, amenities, photos) to separate personal attributes from the real estate data.
- **Preferences:** An entity contained within the `User` (via Composition), managing specific lifestyle traits and constraints.
- **Match:** An entity representing a successful mutual connection established between two users.

## 🚀 7. Two Main Use Cases

1. **Lazy Priority Search:** The recommendation engine calculates and loads only the next best candidate into memory (utilizing Generators and a priority queue). This allows the user to continuously swipe through numerous profiles without experiencing data-loading bottlenecks.
2. **Early Constraint Enforcement (Pipeline Filtering):** If a user defines a strict constraint (e.g., severely allergic to cats or a strict budget cap), the data pipeline filters out non-compliant profiles at an early stage. This prevents the system from suggesting profiles that might have a high overall Match Score but contain an absolute deal-breaker.

## 🔮 8. Future Expansion Idea

Integrating a third-party service (such as the Google Maps API) to automatically calculate public transit commute times from a proposed apartment to the seeker's university campus or workplace, factoring this commute duration directly into the Match Score.