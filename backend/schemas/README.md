# Schemas Module

This directory contains formal **JSON Schema Draft-07** definitions for the **Virtual Wear Simulation** system:

1. **`product.schema.json`**: Product apparel model validation schema (Phase 1.1).
2. **`user_preference.schema.json`**: User preference model validation schema (Phase 1.2).

---

## User Preference Schema (`user_preference.schema.json`)

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
| `location` *(Optional)* | `object` | Required: `country`, `state`, `city` | Geographic user location |
| `climate` *(Optional)* | `string` | Enum: `tropical`, `temperate`, `cold`, `desert`, `coastal` | Local climate zone |
| `favoriteColorsFrequency` *(Optional)* | `object` | Map of color names to integer counts | Interaction frequency by color |
| `interactionMetrics` *(Optional)* | `object` | Required: `productsViewed`, `productsLiked`, `productsPurchased` | Catalog interaction counters |
| `lastPreferenceUpdate` *(Optional)* | `string` | Pattern: ISO 8601 timestamp | Timestamp of last preference update |


---

## Validation Examples

### Validating with Python (`jsonschema`)

```python
import json
import jsonschema

# Load Schema
with open('backend/schemas/user_preference.schema.json', 'r') as f:
    schema = json.load(f)

# Load User Preferences Data
with open('backend/data/user_preferences.json', 'r') as f:
    users = json.load(f)

# Validate each user profile
for index, user in enumerate(users):
    try:
        jsonschema.validate(instance=user, schema=schema)
        print(f"User {user['userId']} is valid.")
    except jsonschema.ValidationError as e:
        print(f"Validation error in user {index}: {e.message}")
```
