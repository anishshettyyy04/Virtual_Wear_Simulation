# REST API Contract Specification — Phase 1.4 Endpoint

## Overview
This document specifies the official API contract for the **Recommendation Engine REST Endpoint** to be implemented in **Phase 1.4 REST APIs & Subsystem Integration**.

---

## Endpoint Specification

### `POST /api/v1/recommendations`

Generates personalized, explainable product recommendations for a target user based on user preferences, physical measurements, and apparel inventory.

---

## 1. Request Header Rules

| Header Name | Required | Allowed Values | Description |
| :--- | :---: | :--- | :--- |
| `Content-Type` | **Yes** | `application/json` | Request payload format |
| `Accept` | No | `application/json` | Desired response format |

---

## 2. Request Body Payload

### Schema (JSON)

```json
{
  "userId": "USR001",
  "limit": 10,
  "forceRefresh": false
}
```

### Parameter Specification

| Parameter | Type | Required | Constraints | Description |
| :--- | :---: | :---: | :--- | :--- |
| **`userId`** | `string` | **Yes** | Pattern: `^USR\d{3}$` | Unique identifier of target user |
| **`limit`** | `integer` | No | Min: 1, Max: 50 (Default: 10) | Maximum number of recommendations to return |
| **`forceRefresh`** | `boolean` | No | Default: `false` | If `true`, bypasses cache and recomputes scores |

---

## 3. Success Response Envelope (HTTP 200 OK)

```json
{
  "success": true,
  "message": "Recommendations generated successfully",
  "engineVersion": "1.0.0",
  "strategy": "RuleBased",
  "configVersion": "1.0",
  "executionTimeMs": 1.85,
  "productsScanned": 25,
  "productsFiltered": 17,
  "recommendationsReturned": 10,
  "userId": "USR001",
  "generatedAt": "2026-07-31T22:37:47.123456+00:00",
  "recommendations": [
    {
      "productId": "TS001",
      "name": "Classic Black Crewneck T-Shirt",
      "category": "tshirt",
      "brand": "Urban Wear",
      "price": 799,
      "currency": "INR",
      "image": "/assets/products/tshirts/ts001.jpg",
      "rating": 4.5,
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

## 4. Error Response Envelopes

### 4.0 User Not Found (HTTP 404 Not Found)

```json
{
  "success": false,
  "message": "User ID 'USR999' not found",
  "engineVersion": "1.0.0",
  "strategy": "RuleBased",
  "configVersion": "1.0",
  "executionTimeMs": 0.5,
  "productsScanned": 25,
  "productsFiltered": 0,
  "recommendationsReturned": 0,
  "userId": "USR999",
  "generatedAt": "2026-07-31T22:37:47.123456+00:00",
  "recommendations": []
}
```

### 4.1 Invalid Request Parameters (HTTP 400 Bad Request)

```json
{
  "success": false,
  "message": "Validation Error: 'userId' field is required",
  "code": "INVALID_REQUEST_PAYLOAD"
}
```

### 4.2 Internal Server Error (HTTP 500 Internal Server Error)

```json
{
  "success": false,
  "message": "Internal Recommendation System Error",
  "code": "INTERNAL_SERVER_ERROR"
}
```

---

## 5. HTTP Status Code Summary

| Status Code | Reason | Description |
| :---: | :--- | :--- |
| **200 OK** | Success | Recommendations computed and returned |
| **400 Bad Request** | User Error | Missing required fields or invalid JSON payload |
| **404 Not Found** | User Error | User profile `userId` does not exist in dataset |
| **500 Server Error** | System Error | Dataset corruption or internal server failure |
