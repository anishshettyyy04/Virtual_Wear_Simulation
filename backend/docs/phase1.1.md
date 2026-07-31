# Technical Documentation — Phase 1.1: Product Data Structure

## Executive Summary
Phase 1.1 establishes the foundational data architecture for the **AI Virtual Wear Simulation** system. It defines a standardized JSON schema, a validated 25-product sample dataset across 8 apparel categories, modular directory structures, and integration specs for downstream subsystems (Recommendation Engine and IDM-VTON AI Virtual Try-On Pipeline).

---

## 1. Product Data Model

Every product entity in the system is represented by 23 standardized attributes:

- **`id`** (`string`): Unique uppercase alphanumeric string (e.g., `TS001`, `KR002`) following pattern `^[A-Z]{2,4}\d{3}$`. Serves as the primary key.
- **`name`** (`string`): Human-readable display title of the apparel item.
- **`category`** (`string`): Standardized lowercase enum representing the product type (`tshirt`, `shirt`, `jeans`, `jacket`, `hoodie`, `dress`, `kurta`, `pants`).
- **`brand`** (`string`): Brand or manufacturer name.
- **`price`** (`number`): Retail price in local currency (`exclusiveMinimum: 0`).
- **`currency`** (`string`): Standard ISO currency code (fixed to `"INR"`).
- **`sizes`** (`array[string]`): Non-empty array of available garment sizes (`S`, `M`, `L`, `XL`, `38`, `40`, `30`, `32`, etc.).
- **`colors`** (`array[string]`): Available color variations.
- **`material`** (`string`): Textile fabric composition (e.g., `100% Premium Cotton`, `Denim`, `Chanderi Silk`).
- **`fit`** (`string`): Standardized fit classification (`slim`, `regular`, `relaxed`, `oversized`).
- **`style`** (`string`): Standardized fashion genre (`casual`, `formal`, `streetwear`, `ethnic`, `sports`).
- **`occasion`** (`string`): Recommended wearing context (e.g., `Daily Wear`, `Office & Meetings`, `Festive & Wedding`).
- **`gender`** (`string`): Demographic target (`men`, `women`, `unisex`).
- **`season`** (`string`): Seasonality recommendation (`summer`, `winter`, `monsoon`, `all-season`).
- **`image`** (`string`): Relative asset path to high-resolution product image (`/assets/products/{category}/{filename}.jpg`).
- **`thumbnail`** (`string`): Relative asset path to compressed thumbnail image (`/assets/products/{category}/{filename}_thumb.jpg`).
- **`description`** (`string`): Detailed textual summary of features, cut, and feel.
- **`rating`** (`number`): Average customer review score (`minimum: 0`, `maximum: 5`).
- **`stock`** (`integer`): Real-time inventory count (`minimum: 0`).
- **`tags`** (`array[string]`): Descriptive keywords for search indexing and NLP tag-matching.
- **`isAvailable`** (`boolean`): Flag indicating if item is active and purchaseable.
- **`createdAt`** (`string`): ISO 8601 creation timestamp.
- **`updatedAt`** (`string`): ISO 8601 last modification timestamp.

---

## 2. Folder Structure

```
backend/
├── assets/
│   └── products/
│       ├── tshirts/      # High-res images & thumbnails for tshirts
│       ├── shirts/       # High-res images & thumbnails for shirts
│       ├── jeans/        # High-res images & thumbnails for jeans
│       ├── jackets/      # High-res images & thumbnails for jackets
│       ├── hoodies/      # High-res images & thumbnails for hoodies
│       ├── dresses/      # High-res images & thumbnails for dresses
│       ├── kurtas/       # High-res images & thumbnails for kurtas
│       └── pants/        # High-res images & thumbnails for pants
├── data/
│   ├── products.json     # 25-item seed dataset
│   └── README.md         # Dataset statistics and migration notes
├── schemas/
│   ├── product.schema.json # JSON Schema Draft-07 specification
│   └── README.md         # Schema constraints and validation rules
└── docs/
    └── phase1.1.md       # Technical specification & architecture docs
```

---

## 3. Schema Design & Constraints

The schema enforced in `backend/schemas/product.schema.json` guarantees strict data integrity:
1. **Strict Field Requirements**: All 23 attributes are mandatory (`required`). Missing fields fail validation instantly.
2. **No Extra Attributes**: `additionalProperties: false` ensures no unauthorized or un-sanitized fields enter the pipeline.
3. **Numeric Bounds**:
   - `price` > 0 (`exclusiveMinimum: 0`)
   - `rating` ∈ [0.0, 5.0] (`minimum: 0, maximum: 5`)
   - `stock` ≥ 0 (`minimum: 0`)
4. **Standardized Enums**:
   - `category`: `tshirt`, `shirt`, `jeans`, `jacket`, `hoodie`, `dress`, `kurta`, `pants`
   - `fit`: `slim`, `regular`, `relaxed`, `oversized`
   - `style`: `casual`, `formal`, `streetwear`, `ethnic`, `sports`
   - `season`: `summer`, `winter`, `monsoon`, `all-season`
   - `gender`: `men`, `women`, `unisex`

---

## 4. Recommendation Engine Compatibility

The product data model is designed for direct integration with content-based filtering, collaborative filtering, and vector similarity recommendation systems:

| Field | Usage | Subsystem Integration |
| :--- | :--- | :--- |
| `category` | Filtering | Hard filtering on catalog navigation and category-specific recommendations |
| `style` | Recommendation | Content-based style affinity scoring (e.g. user prefers `streetwear`) |
| `fit` | Recommendation | User body shape matching and fit preference filtering |
| `occasion` | Recommendation | Contextual event-based outfits (e.g. recommending `formal` items for Office) |
| `image` | AI Try-On | Input garment image feed for image feature extractor & IDM-VTON pipeline |
| `colors` | Matching | Color harmony & complementary outfit matching matrix |
| `material` | Search | Material search filter and tactile preference matching |
| `tags` | AI Recommendation | Vector embeddings & TF-IDF similarity search across product catalog |

---

## 5. AI Try-On Compatibility (IDM-VTON Integration)

The dataset and schema are fully optimized for seamless ingestion into the **IDM-VTON (Image-Based Virtual Try-On Network)** pipeline:

### 5.1 Garment Category Mapping for Parsing & Masking
IDM-VTON requires classifying garments into specific pose-masking zones:
- **Upper Garments** (`category`: `tshirt`, `shirt`, `jacket`, `hoodie`, `kurta`): Maps to IDM-VTON `upper_body` mask generator. Masking isolates torso and arm regions.
- **Lower Garments** (`category`: `jeans`, `pants`): Maps to IDM-VTON `lower_body` mask generator. Masking isolates hips and leg regions.
- **Full Garments** (`category`: `dress`): Maps to IDM-VTON `dresses` / `overall` mask generator. Masking covers full body torso down to knee/ankle.

### 5.2 Image & Asset Pipelines
- **Resolution**: Garment images linked via `image` are stored in uniform aspect ratios suitable for 768x1024 / 512x384 UNet conditioning inputs.
- **Alpha Mask Extraction**: Transparent PNG or pre-segmented background images are referenced from `/assets/products/{category}/` to bypass real-time background removal overhead during inference.
