# Technical Documentation — Phase 1.3: Recommendation Engine

## Executive Summary
Phase 1.3 implements the **Recommendation Engine** for the **AI Virtual Wear Simulation** system. It connects the Phase 1.1 Product Dataset (`products.json`) and Phase 1.2 User Preference Model (`user_preferences.json`) into a production-ready, modular recommendation pipeline. The engine performs hard filtering, weighted attribute scoring, personalization boosts, score normalization to [0, 100], and explainable recommendation reason generation.

---

## 1. Recommendation Pipeline Architecture

```
                 ┌──────────────────────────┐
                 │  products.json (Seed)    │
                 └────────────┬─────────────┘
                              │
                              ▼
┌───────────────────────────────────────────────────────────┐
│              RecommendationEngine.recommend()             │
└─────────────────────────────┬─────────────────────────────┘
                              │
               ┌──────────────┴──────────────┐
               │  user_preferences.json      │
               └──────────────┬──────────────┘
                              │
                              ▼
┌───────────────────────────────────────────────────────────┐
│ Step 1: Pre-Filtering (filters.py)                        │
│   - Availability & Stock Check (isAvailable, stock > 0)   │
│   - Gender Compatibility (men/women/unisex)               │
│   - Budget Boundary Check (min <= price <= max)           │
└─────────────────────────────┬─────────────────────────────┘
                              │
                              ▼
┌───────────────────────────────────────────────────────────┐
│ Step 2: Weighted Attribute Scoring (scorer.py)            │
│   - Category (35%), Style (20%), Color (15%),             │
│     Brand (10%), Fit (10%), Budget (10%)                  │
│   - Personalization Boosts: Wishlist (+10), Purchase      │
│     History (+5), Climate (+5), Rating (+5),              │
│     Recommendation History Penalty (-15)                  │
│   - Score Normalization: Clamp to [0, 100]                │
└─────────────────────────────┬─────────────────────────────┘
                              │
                              ▼
┌───────────────────────────────────────────────────────────┐
│ Step 3: Explainable Reason Generation (explain.py)         │
│   - Generate human-readable reason strings                │
└─────────────────────────────┬─────────────────────────────┘
                              │
                              ▼
┌───────────────────────────────────────────────────────────┐
│ Step 4: O(n log n) Ranking & Deduplication (engine.py)    │
│   - Sort candidates descending by normalized score         │
│   - Enforce unique product IDs and output limit           │
└─────────────────────────────┬─────────────────────────────┘
                              │
                              ▼
┌───────────────────────────────────────────────────────────┐
│ Output Response Envelope                                  │
│ { userId, generatedAt, totalRecommendations,              │
│   recommendations: [{ productId, score, reasons, ... }] } │
└───────────────────────────────────────────────────────────┘
```

---

## 2. Scoring Formula & Weights

The base recommendation score is calculated out of 100 points using the following weights:

| Attribute | Base Weight | Scoring Calculation |
| :--- | :---: | :--- |
| **Category** | **35** | Full points if `product.category` ∈ `user.preferredCategories` |
| **Style** | **20** | Full points if `product.style` ∈ `user.preferredStyles` |
| **Color** | **15** | Overlap ratio between `product.colors` and `user.preferredColors` + frequency boost (`favoriteColorsFrequency`) |
| **Brand** | **10** | Full points if `product.brand` ∈ `user.preferredBrands` |
| **Fit** | **10** | Full points if `product.fit` == `user.preferredFit` |
| **Budget** | **10** | Maximum near mid-point of budget range; scales down towards boundaries |

---

## 3. Advanced Personalization Dynamics

The scorer applies dynamic adjustments on top of base attribute scores:

1. **Wishlist Boost (+10 points)**: Items saved in `user.wishlist` receive an immediate score boost.
2. **Purchase History Boost (+5 points)**: Items sharing brand or style with previous purchases receive an affinity boost.
3. **Climate & Weather Alignment (+5 points)**: `climate` zone matching adjusts material scoring (e.g., linen in `tropical`, fleece in `cold`).
4. **Customer Rating Boost (+5 points)**: High customer ratings (≥ 4.5★) receive a quality boost.
5. **Recommendation Recency Penalty (-15 points)**: Items present in `user.recommendationHistory` are penalized to prevent repetitive recommendations.

---

## 4. Explainable Recommendations

For every recommended product, `RecommendationExplainer` generates human-readable reasoning strings.

### Example Output

```json
{
  "userId": "USR001",
  "generatedAt": "2026-07-31T22:28:15Z",
  "totalRecommendations": 1,
  "recommendations": [
    {
      "productId": "TS001",
      "name": "Classic Black Crewneck T-Shirt",
      "category": "tshirt",
      "brand": "Urban Wear",
      "price": 799,
      "currency": "INR",
      "image": "/assets/products/tshirts/ts001.jpg",
      "score": 94.5,
      "reasons": [
        "Matches preferred category (tshirt)",
        "Matches preferred style (casual)",
        "Within your budget",
        "Preferred color (Black)",
        "Favored brand (Urban Wear)",
        "Matches preferred fit (regular)",
        "Available in your size (M, L)",
        "Suitable for tropical climate",
        "Highly rated product (4.5★)"
      ]
    }
  ]
}
```

---

## 5. Configuration System

The recommendation engine dynamically loads settings from [`backend/config/recommendation_config.json`](file:///c:/Users/Gagan/OneDrive/Desktop/Virtual_Wear_Simulation/backend/config/recommendation_config.json):
- **Attribute Weights**: Category (35), Style (20), Color (15), Brand (10), Fit (10), Budget (10).
- **Personalization Boosts**: Wishlist (15), Purchase History (10), Favorite Color (5), Climate (5).
- **Penalties**: Recommendation History (10).
- **Output Limits**: Max recommendations default (10).

---

## 6. Strategy Pattern Architecture

Exposed under `backend/recommendation/strategies/`:
- **`RuleBasedStrategy`**: Active rule-based pre-filtering, attribute scoring, and ranking engine.
- **`CollaborativeStrategy`**: Placeholder interface for User-User KNN / SVD Matrix Factorization.
- **`ContentBasedStrategy`**: Placeholder interface for TF-IDF / CLIP visual vector embeddings.
- **`HybridStrategy`**: Placeholder interface for ensembled multi-model recommendation.

---

## 7. Performance Metrics & Monitoring

Every recommendation response payload includes high-precision execution metrics:
- **`executionTimeMs`**: Milliseconds taken to execute filtering, scoring, and ranking.
- **`productsScanned`**: Count of total products evaluated from catalog.
- **`productsFiltered`**: Count of candidates passing mandatory hard filters.
- **`recommendationsReturned`**: Count of final recommendations in envelope.

---

## 8. Logging System

Centralized logging provided by `backend/utils/logger.py`:
- **`INFO`**: Logs request initialization, dataset loading, and execution summary.
- **`WARNING`**: Logs missing configuration files or unrecognized user IDs.
- **`ERROR`**: Logs dataset parsing exceptions or file missing errors.

---

## 9. Recommendation Analytics

Analytics utilities in `backend/recommendation/analytics.py`:
- `compute_most_recommended_products()`
- `compute_average_recommendation_score()`
- `compute_category_popularity()`
- `compute_recommendation_frequency()`
- `compute_user_preference_distribution()`

---

## 11. Cache System

Implemented in [`backend/cache/recommendation_cache.py`](file:///c:/Users/Gagan/OneDrive/Desktop/Virtual_Wear_Simulation/backend/cache/recommendation_cache.py):
- **In-memory cache**: Keyed by `userId` to eliminate redundant scoring recalculations.
- **Configurable TTL**: Default 300 seconds loaded from `recommendation_config.json`.
- **Automatic Expiration & Invalidation**: Purges expired entries automatically and exposes `invalidate(user_id)`.
- **Hit/Miss Statistics**: Tracks hit rate percentage and active entries.

---

## 12. Recommendation Versioning

Every response payload contains semantic versioning metadata:
- **`engineVersion`**: `"1.0.0"`
- **`strategy`**: `"RuleBased"`
- **`configVersion`**: `"1.0"`

Enforced by Draft-07 JSON Schema [`backend/schemas/recommendation.schema.json`](file:///c:/Users/Gagan/OneDrive/Desktop/Virtual_Wear_Simulation/backend/schemas/recommendation.schema.json).

---

## 13. Health Monitoring Subsystem

Exposed via [`backend/recommendation/health.py`](file:///c:/Users/Gagan/OneDrive/Desktop/Virtual_Wear_Simulation/backend/recommendation/health.py) function `check_system_health()`:
- Verifies product dataset, user dataset, configuration file, strategy initialization, cache layer, and analytics module availability.

---

## 14. Recommendation History Manager

Implemented in [`backend/recommendation/history.py`](file:///c:/Users/Gagan/OneDrive/Desktop/Virtual_Wear_Simulation/backend/recommendation/history.py):
- Saves historical recommendation timestamps to prevent repetitive suggestions across sessions.
- Automatically purges stale history entries older than configurable threshold (30 days).

---

## 15. Benchmarking & Performance Utility

Implemented in [`backend/scripts/benchmark_recommendation.py`](file:///c:/Users/Gagan/OneDrive/Desktop/Virtual_Wear_Simulation/backend/scripts/benchmark_recommendation.py):
- Measures average latency (ms), recommendations per second, processed catalog count, and cache hit rate (50%-91%+).
- Exports metrics to [`backend/data/recommendation_metrics.json`](file:///c:/Users/Gagan/OneDrive/Desktop/Virtual_Wear_Simulation/backend/data/recommendation_metrics.json).

---

## 16. API Contract Documentation

Documented in [`backend/docs/api-contract.md`](file:///c:/Users/Gagan/OneDrive/Desktop/Virtual_Wear_Simulation/backend/docs/api-contract.md) detailing request parameters, response schemas, error envelopes, and HTTP status codes for Phase 1.4 REST endpoint `POST /api/v1/recommendations`.


