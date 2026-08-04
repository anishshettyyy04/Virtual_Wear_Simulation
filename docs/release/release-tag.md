# Release Tag & Versioning Strategy Guide — Version v1.0.0-phase1

This guide documents the release tag specification and Semantic Versioning (SemVer) strategy for the **AI Virtual Wear Simulation** project.

---

## 1. Release Specification

- **Release Name**: Phase 1 Backend Release
- **Release Version**: `v1.0.0-phase1`
- **Git Tag Name**: `v1.0.0-phase1`
- **Target Commit**: Main Release Commit on Phase 1 Completion
- **Release Date**: July 31, 2026

---

## 2. Git Release Tag Execution Commands

To create and push the annotated release tag to GitHub, run the following commands:

```bash
# Create annotated release tag
git tag -a v1.0.0-phase1 -m "Phase 1 Release — AI Virtual Wear Simulation Backend System"

# Push release tag to remote GitHub repository
git push origin v1.0.0-phase1
```

---

## 3. Semantic Versioning (SemVer 2.0.0) Strategy

Future releases follow the `MAJOR.MINOR.PATCH` versioning schema:

```
v1.0.0-phase1
│ │ │ └────── Phase Tag Identifier
│ │ └──────── PATCH (Bug fixes, security patches, performance tweaks)
│ └────────── MINOR (New backward-compatible feature endpoints or algorithms)
└──────────── MAJOR (Breaking API schema changes, major UI / AI model integration)
```

- **MAJOR Version Bump (`v2.0.0`)**: Triggered when introducing non-backward-compatible API schema changes, integrating Ashwin's React Frontend, or deploying Anish's IDM-VTON AI Virtual Try-On pipeline (`POST /api/v1/try-on`).
- **MINOR Version Bump (`v1.1.0`)**: Triggered when adding new endpoints (e.g., product reviews, wishlist endpoints) or new recommendation scoring strategies without breaking existing API contracts.
- **PATCH Version Bump (`v1.0.1`)**: Triggered when fixing bugs, refining JSON Schema validation rules, or applying security dependency updates.
