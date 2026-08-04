# Schemas Module

This directory contains formal **JSON Schema Draft-07** definitions for the **Virtual Wear Simulation** system:

1. **`product.schema.json`**: Product apparel model validation schema (Phase 1.1).
2. **`user_preference.schema.json`**: User preference model validation schema (Phase 1.2).
3. **`recommendation.schema.json`**: Recommendation request/response payload validation schema (Phase 1.3).

---

## 1. Product Schema (`product.schema.json`)

### Properties & Validation Rules

| Property | Type | Constraints / Enums | Description |
| :--- | :--- | :--- | :--- |
| `id` | `string` | Pattern: `^[A-Z]{2,4}\d{3}$` | Unique identifier code (e.g., `TS001`, `JN002`) |
| `name` | `string` | Min length: 1 | Non-empty product title |
| `category` | `string` | Enum: `tshirt`, `shirt`, `jeans`, `jacket`, `hoodie`, `dress`, `kurta`, `pants` | Standardized apparel category |
| `brand` | `string` | Min length: 1 | Brand or manufacturer name |
| `price` | `number` | `exclusiveMinimum: 0` | Price strictly greater than 0 |
| `currency` | `string` | Enum: `INR` | ISO currency code |
| `sizes` | `array` | Min items: 1, `uniqueItems: true` | Array of available size strings |
| `colors` | `array` | Min items: 1, `uniqueItems: true` | Array of available color strings |
| `material` | `string` | Min length: 1 | Fabric composition description |
| `fit` | `string` | Enum: `slim`, `regular`, `relaxed`, `oversized` | Standardized fit style |
| `style` | `string` | Enum: `casual`, `formal`, `streetwear`, `ethnic`, `sports` | Fashion category style |
| `occasion` | `string` | Min length: 1 | Intended wearing occasion |
| `gender` | `string` | Enum: `men`, `women`, `unisex` | Target gender demographic |
| `season` | `string` | Enum: `summer`, `winter`, `monsoon`, `all-season` | Seasonality recommendation |
| `image` | `string` | Pattern: `^/assets/products/[a-z]+/[a-z0-9_-]+\.(jpg\|jpeg\|png\|webp)$` | Relative path to main image |
| `thumbnail` | `string` | Pattern: `^/assets/products/[a-z]+/[a-z0-9_-]+\.(jpg\|jpeg\|png\|webp)$` | Relative path to thumbnail |
| `description` | `string` | Min length: 1 | Textual product description |
| `rating` | `number` | `minimum: 0`, `maximum: 5` | Customer rating between 0 and 5 |
| `stock` | `integer` | `minimum: 0` | Available stock count (>= 0) |
| `tags` | `array` | Min items: 1, `uniqueItems: true` | Search and recommendation tags |
| `isAvailable` | `boolean` | `true` or `false` | Product availability status |
| `createdAt` | `string` | Pattern: ISO 8601 timestamp | Creation date timestamp |
| `updatedAt` | `string` | Pattern: ISO 8601 timestamp | Last modified timestamp |

---

## 2. User Preference Schema (`user_preference.schema.json`)

### Properties & Validation Rules

| Property | Type | Constraints / Enums | Description |
| :--- | :--- | :--- | :--- |
| `userId` | `string` | Pattern: `^USR\d{3}$` | Unique user identifier code |
| `name` | `string` | Min length: 1 | Full name of the user |
| `gender` | `string` | Enum: `men`, `women`, `unisex` | Gender demographic |
| `ageGroup` | `string` | Enum: `teen`, `adult`, `senior` | Age group classification |
| `preferredCategories` | `array` | Min items: 1, Enum items: `tshirt`, `shirt`, `jeans`, `jacket`, `hoodie`, `dress`, `kurta`, `pants` | Preferred apparel categories |
| `preferredColors` | `array` | Min items: 1 | Preferred color choices |
| `preferredStyles` | `array` | Min items: 1, Enum items: `casual`, `formal`, `streetwear`, `ethnic`, `sports` | Preferred fashion styles |
| `preferredFit` | `string` | Enum: `slim`, `regular`, `relaxed`, `oversized` | Preferred cut / fit type |
| `preferredBrands` | `array` | Min items: 1 | Preferred apparel brands |
| `preferredMaterials` | `array` | Min items: 1 | Preferred fabric compositions |
| `preferredOccasions` | `array` | Min items: 1 | Preferred wearing occasions |
| `preferredSeasons` | `array` | Min items: 1, Enum items: `summer`, `winter`, `monsoon`, `all-season` | Preferred seasonal apparel |
| `budgetRange` | `object` | Required: `min`, `max` (`min` >= 0, `max` > `min`) | Price range boundaries |
| `budgetTier` | `string` | Enum: `low`, `medium`, `premium` | Budget tier classification |
| `favoriteSizes` | `array` | Min items: 1 | Favorite clothing size codes |
| `height` | `number` | `exclusiveMinimum: 0` | User height in cm |
| `weight` | `number` | `exclusiveMinimum: 0` | User weight in kg |
| `bodyType` | `string` | Enum: `slim`, `athletic`, `regular`, `curvy`, `plus-size` | User body build type |
| `wishlist` | `array` | Unique items, Pattern: `^[A-Z]{2,4}\d{3}$` | Product IDs in wishlist |
| `purchaseHistory` | `array` | Unique items, Pattern: `^[A-Z]{2,4}\d{3}$` | Purchased product IDs |
| `recommendationHistory` | `array` | Unique items, Pattern: `^[A-Z]{2,4}\d{3}$` | Recommended product IDs |
| `createdAt` | `string` | Pattern: ISO 8601 timestamp | Profile creation date |
| `updatedAt` | `string` | Pattern: ISO 8601 timestamp | Last modification date |

---

## 3. Usage & Automated Validation Examples

### Validating with Python (`jsonschema`)

```python
import json
import jsonschema

# Load Schema
with open('backend/schemas/product.schema.json', 'r') as f:
    schema = json.load(f)

# Load Data
with open('backend/data/products.json', 'r') as f:
    products = json.load(f)

# Validate each product
for index, product in enumerate(products):
    try:
        jsonschema.validate(instance=product, schema=schema)
        print(f"Product {product['id']} is valid.")
    except jsonschema.ValidationError as e:
        print(f"Validation error in product {index}: {e.message}")
```

### Validating with Node.js (`Ajv`)

```javascript
const fs = require('fs');
const Ajv = require('ajv');
const addFormats = require('ajv-formats');

const ajv = new Ajv({ allErrors: true });
addFormats(ajv);

const schema = JSON.parse(fs.readFileSync('backend/schemas/product.schema.json', 'utf8'));
const products = JSON.parse(fs.readFileSync('backend/data/products.json', 'utf8'));

const validate = ajv.compile(schema);

products.forEach((product, idx) => {
  const valid = validate(product);
  if (!valid) {
    console.error(`Validation failed for product ${product.id || idx}:`, validate.errors);
  } else {
    console.log(`Product ${product.id} passed validation.`);
  }
});
```
