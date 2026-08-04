# AI Virtual Try-On Service Integration Guide — IDM-VTON Subsystem

Welcome to the AI Virtual Try-On integration guide for the **AI Virtual Wear Simulation** project! This guide is prepared specifically for **Anish** to integrate the IDM-VTON (Image-Based Virtual Try-On) diffusion pipeline with the Python FastAPI Backend.

---

## 1. Subsystem Architecture Overview

```
┌───────────────────────┐            ┌───────────────────────────────┐            ┌─────────────────────────────┐
│  Personalization API  │ ─────────> │   Product & Image Catalog     │ ─────────> │   IDM-VTON AI Pipeline      │
│  (Phase 1.3/1.4 Engine)│            │  (/assets/products/...)       │            │  (Garment + Person Try-On)  │
└───────────────────────┘            └───────────────────────────────┘            └─────────────────────────────┘
```

---

## 2. Product Metadata & Garment Asset Paths

All product items in `products.json` include explicit asset paths and category mapping required by IDM-VTON:

```json
{
  "id": "TS001",
  "name": "Classic Black Crewneck T-Shirt",
  "category": "tshirt",
  "gender": "unisex",
  "sizes": ["S", "M", "L", "XL"],
  "image": "/assets/products/tshirts/ts001.jpg"
}
```

---

## 3. User Body Measurement & Profile Metrics

User preferences stored in `user_preferences.json` supply body build attributes for 3D human pose mapping and mesh warps:

```json
{
  "userId": "USR001",
  "gender": "men",
  "height": 178.0,
  "weight": 72.0,
  "bodyType": "regular",
  "favoriteSizes": ["M", "L"],
  "preferredFit": "regular"
}
```

---

## 4. Category Mapping Matrix for IDM-VTON

| Backend Category | IDM-VTON Garment Type | Masking Region | Target Category |
| :--- | :--- | :--- | :--- |
| `tshirt` | `upper_body` | Torso & Shoulders | Topwear |
| `shirt` | `upper_body` | Torso & Arms | Topwear |
| `jacket` | `upper_body` | Upper Body Layer | Outerwear |
| `jeans` | `lower_body` | Waist to Ankle | Bottomwear |
| `trousers` | `lower_body` | Waist to Ankle | Bottomwear |

---

## 5. Planned AI Try-On Endpoint Specification (`POST /api/v1/try-on`)

The future Phase 2.0 REST endpoint will accept multipart user image upload and target `productId`:

### Request
- `userId` (form-data / string): Target user identifier
- `productId` (form-data / string): Product garment identifier
- `personImage` (form-data / file): JPEG/PNG user photograph

### Expected Response
```json
{
  "success": true,
  "message": "Virtual try-on simulation generated successfully",
  "data": {
    "tryOnId": "VTON_987654321",
    "userId": "USR001",
    "productId": "TS001",
    "resultImageUrl": "/assets/tryon/renders/vton_usr001_ts001.jpg",
    "confidenceScore": 0.96,
    "processingTimeMs": 1420.5
  },
  "timestamp": "2026-07-31T23:00:00Z",
  "requestId": "e1f2a3b4-c5d6-7e8f-9a0b-1c2d3e4f5a6b"
}
```
