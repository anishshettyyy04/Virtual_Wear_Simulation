# Backend Product Data Module

This directory contains the core sample clothing dataset used across the **Virtual Wear Simulation** project, including the Recommendation Engine, AI Virtual Try-On pipeline, and frontend product catalog.

---

## Dataset Statistics

Total Products: 25

Categories:
T-Shirts
Shirts
Jeans
Jackets
Hoodies
Dresses
Kurtas
Pants

---

## Category Distribution

| Category | Enum Key | Product Count | ID Range |
| :--- | :--- | :---: | :--- |
| **T-Shirts** | `tshirt` | 3 | `TS001` – `TS003` |
| **Shirts** | `shirt` | 3 | `SH001` – `SH003` |
| **Jeans** | `jeans` | 3 | `JN001` – `JN003` |
| **Jackets** | `jacket` | 3 | `JK001` – `JK003` |
| **Hoodies** | `hoodie` | 3 | `HD001` – `HD003` |
| **Dresses** | `dress` | 3 | `DR001` – `DR003` |
| **Kurtas** | `kurta` | 4 | `KR001` – `KR004` |
| **Pants** | `pants` | 3 | `PN001` – `PN003` |

---

## Supported Attributes & Conventions

- **Currency**: `INR` (Indian Rupee) across all products.
- **Sizes**: Standardized size codes per category:
  - Apparel/Tees/Dresses/Hoodies: `XS`, `S`, `M`, `L`, `XL`
  - Formal Shirts/Kurtas: `38`, `40`, `42`, `44`
  - Jeans/Pants: `28`, `30`, `32`, `34`, `36`
- **Media Paths**:
  - Image: `/assets/products/{category}/{id_lowercase}.jpg`
  - Thumbnail: `/assets/products/{category}/{id_lowercase}_thumb.jpg`

---

## Directory Structure

```
backend/
├── assets/
│   └── products/
│       ├── tshirts/
│       ├── shirts/
│       ├── jeans/
│       ├── jackets/
│       ├── hoodies/
│       ├── dresses/
│       ├── kurtas/
│       └── pants/
└── data/
    ├── products.json
    └── README.md
```

---

## Sample Product Entity

```json
{
  "id": "TS001",
  "name": "Classic Black Crewneck T-Shirt",
  "category": "tshirt",
  "brand": "Urban Wear",
  "price": 799,
  "currency": "INR",
  "sizes": ["S", "M", "L", "XL"],
  "colors": ["Black"],
  "material": "100% Premium Cotton",
  "fit": "regular",
  "style": "casual",
  "occasion": "Daily Wear",
  "gender": "unisex",
  "season": "all-season",
  "image": "/assets/products/tshirts/ts001.jpg",
  "thumbnail": "/assets/products/tshirts/ts001_thumb.jpg",
  "description": "Soft breathable cotton t-shirt with reinforced crew neck and classic fit.",
  "rating": 4.5,
  "stock": 35,
  "tags": ["tshirt", "cotton", "black", "basic", "crewneck"],
  "isAvailable": true,
  "createdAt": "2026-01-15T10:00:00Z",
  "updatedAt": "2026-01-15T10:00:00Z"
}
```

---

## Future Database Migration Plan

This JSON file acts as an initial seed dataset. As the system scales:
1. **Document Database (MongoDB/PostgreSQL with JSONB)**: `products.json` maps 1:1 with a `Product` document collection/table schema.
2. **Search Indexing**: `tags`, `name`, `material`, and `description` can be ingested into Elasticsearch or PostgreSQL Full-Text Search.
3. **Vector Store**: `image` and `tags` can be embedded into vector databases (Qdrant, Pinecone) for AI-driven visual recommendations and similarity searches.
