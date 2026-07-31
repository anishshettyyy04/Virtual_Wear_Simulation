# Technical Documentation — Phase 1.2: User Preference Model

## Executive Summary
Phase 1.2 establishes the **User Preference Model** for the **AI Virtual Wear Simulation** system. It defines a validated JSON Schema (`user_preference.schema.json`), a 12-profile sample user dataset (`user_preferences.json`), automated cross-reference validation scripts (`validate_user_preferences.py`), and technical specifications for recommendation engine weighting and IDM-VTON AI Virtual Try-On body metric preprocessing.

---

## 1. User Preference Model Overview

The User Preference Model encapsulates user fashion tastes, physical body measurements, budget tiers, brand affinities, and interaction history (`wishlist`, `purchaseHistory`, `recommendationHistory`) into a unified entity.

### Field Descriptions

- **`userId`** (`string`): Unique user identifier code (e.g., `USR001`, `USR012`) matching pattern `^USR\d{3}$`.
- **`name`** (`string`): Full name of the user.
- **`gender`** (`string`): Demographic classification (`men`, `women`, `unisex`).
- **`ageGroup`** (`string`): Age demographic classification (`teen`, `adult`, `senior`).
- **`preferredCategories`** (`array[string]`): Categories the user prefers to browse and buy (`tshirt`, `shirt`, `jeans`, `jacket`, `hoodie`, `dress`, `kurta`, `pants`).
- **`preferredColors`** (`array[string]`): List of favored garment colors.
- **`preferredStyles`** (`array[string]`): Preferred fashion genres (`casual`, `formal`, `streetwear`, `ethnic`, `sports`).
- **`preferredFit`** (`string`): Favored garment cut (`slim`, `regular`, `relaxed`, `oversized`).
- **`preferredBrands`** (`array[string]`): List of favored apparel brands.
- **`preferredMaterials`** (`array[string]`): Favored fabric compositions (e.g., `100% Premium Cotton`, `Chanderi Silk`).
- **`preferredOccasions`** (`array[string]`): Target wearing occasions (e.g., `Daily Wear`, `Office & Meetings`, `Festive & Wedding`).
- **`preferredSeasons`** (`array[string]`): Favored seasonality (`summer`, `winter`, `monsoon`, `all-season`).
- **`budgetRange`** (`object`): Price boundaries `{ "min": 500, "max": 3000 }` in local currency (`INR`).
- **`budgetTier`** (`string`): Budget classification tier (`low`, `medium`, `premium`).
- **`favoriteSizes`** (`array[string]`): Array of sizes standard to the user (e.g., `S`, `M`, `L`, `32`, `40`).
- **`height`** (`number`): User height in centimeters (e.g., `178.0`).
- **`weight`** (`number`): User weight in kilograms (e.g., `72.0`).
- **`bodyType`** (`string`): Build classification (`slim`, `athletic`, `regular`, `curvy`, `plus-size`).
- **`wishlist`** (`array[string]`): Array of saved product IDs from Phase 1.1 (`TS001`, `JN001`).
- **`purchaseHistory`** (`array[string]`): Array of previously purchased product IDs.
- **`recommendationHistory`** (`array[string]`): Array of previously recommended product IDs.
- **`location`** (`object` [Optional]): User geographic location `{ "country": "India", "state": "Karnataka", "city": "Bengaluru" }`.
- **`climate`** (`string` [Optional]): Local climate classification (`tropical`, `temperate`, `cold`, `desert`, `coastal`).
- **`favoriteColorsFrequency`** (`object` [Optional]): Frequency counter of color interactions (e.g. `{ "black": 18, "grey": 12 }`).
- **`interactionMetrics`** (`object` [Optional]): Engagement counters `{ "productsViewed": 125, "productsLiked": 42, "productsPurchased": 9 }`.
- **`lastPreferenceUpdate`** (`string` [Optional]): ISO 8601 timestamp of last explicit or implicit preference update.
- **`createdAt`** (`string`): ISO 8601 creation timestamp.
- **`updatedAt`** (`string`): ISO 8601 modification timestamp.

---

## 2. Folder Structure

```
backend/
├── data/
│   ├── products.json            # 25-item Phase 1.1 product dataset
│   ├── user_preferences.json    # 12-item Phase 1.2 user preference dataset
│   └── README.md
├── schemas/
│   ├── product.schema.json       # Phase 1.1 product schema
│   ├── user_preference.schema.json # Phase 1.2 user preference schema
│   └── README.md
├── docs/
│   ├── phase1.1.md
│   └── phase1.2.md               # Technical architecture & integration doc
└── scripts/
    ├── validate_products.py
    └── validate_user_preferences.py # Cross-validation script
```

---

## 3. Schema Design & Constraints

Defined in `backend/schemas/user_preference.schema.json`:
1. **Strict Validation**: All 23 core attributes are mandatory (`required`).
2. **Backward Compatible Extensions**: Optional fields (`location`, `climate`, `favoriteColorsFrequency`, `interactionMetrics`, `lastPreferenceUpdate`) extend user profiles without breaking baseline schema validation.
3. **Budget Range & Tier Rules**:
   - `budgetRange.min` ≥ 0
   - `budgetRange.max` > `budgetRange.min`
   - `budgetTier` ∈ [`low`, `medium`, `premium`]
4. **Reference Integrity**: Product IDs in `wishlist`, `purchaseHistory`, and `recommendationHistory` must strictly exist in `products.json`.
5. **Enum Alignment**: Enums strictly mirror Phase 1.1 product dataset standards.

---

## 4. Recommendation Strategy & Weights

The User Preference Model integrates into the upcoming **Phase 1.3 Recommendation Engine** via weighted similarity scoring:

| Preference | Weight | Integration Mechanism |
| :--- | :---: | :--- |
| **Category** | **35%** | Hard filter and primary candidate retrieval weight |
| **Style** | **20%** | Content-based style vector similarity score |
| **Color** | **15%** | Color affinity matrix & frequency count (`favoriteColorsFrequency`) |
| **Brand** | **10%** | Brand preference score boost |
| **Fit** | **10%** | Fit cut preference alignment |
| **Budget** | **10%** | Price boundary score penalty for out-of-budget items |

---

## 5. AI Try-On Compatibility (IDM-VTON Integration)

- **`height` & `weight`**: Passed to 3D mesh generator / SMPL body model reconstruction algorithms for realistic body shape synthesis.
- **`bodyType`**: Informs pose mask generator on torso and leg shape estimation during UNet conditioning.
- **`favoriteSizes`**: Provides automatic size selection defaults when rendering try-on apparel.

---

## 6. Personalization Enhancements

- **Interaction History**: Real-time ratio tracking (`productsLiked` / `productsViewed`) dynamically recalculates user category weights.
- **Color Frequency Vectors**: `favoriteColorsFrequency` builds a continuous probability vector for color affinity beyond simple discrete lists.
- **User Location & Climate-Aware Recommendations**: `climate` (`tropical`, `cold`, `desert`, etc.) dynamically boosts seasonal items (e.g. prioritizing linen in tropical zones, fleece in cold zones).

---

## 7. Future AI Capabilities

1. **Recommendation Accuracy**: Multi-armed bandit models utilizing `interactionMetrics` for real-time recommendation exploitation and exploration.
2. **Seasonal & Climate Outfit Suggestions**: Weather API integration matching real-time user `location` and `climate` to generate daily outfit bundles.
3. **Personalized Ranking**: Learning-to-rank (LTR) algorithms scoring candidate items based on historical conversion ratios (`purchaseHistory` vs `wishlist`).
4. **AI Outfit Generation**: Generative AI / LLM agents utilizing user preferences, body metrics, and climate data to compose head-to-toe virtual wear looks.
5. **Analytics & Demand Forecasting**: Aggregated trend analysis on preferred styles, colors, and brands to inform inventory management.

