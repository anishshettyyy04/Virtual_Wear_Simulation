# Contributing to AI Virtual Wear Simulation

Thank you for contributing to the **AI Virtual Wear Simulation** project! We welcome contributions from developers, designers, and AI researchers.

---

## 1. Code of Conduct

All contributors are expected to adhere to our [Code of Conduct](CODE_OF_CONDUCT.md).

---

## 2. Branch Naming Conventions

Never commit work directly to the `main` branch. Create a feature or fix branch from `main`:

```text
feature/<author>-<phase>-<description>
fix/<author>-<description>
chore/<author>-<description>
```

### Examples:
- `feature/gagan-phase1.6-release-enhancements`
- `fix/ashwin-cors-headers`
- `feature/anish-idm-vTON-pipeline`

---

## 3. Commit Message Standards (Conventional Commits)

Commit messages must follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```text
<type>(<scope>): <short summary>
```

### Allowed Types:
- **`feat`**: A new feature or endpoint.
- **`fix`**: A bug fix.
- **`docs`**: Documentation changes only.
- **`test`**: Adding or updating tests.
- **`refactor`**: Code changes that neither fix a bug nor add a feature.
- **`chore`**: Maintenance tasks, version bumps, build script updates.

### Examples:
- `feat(api): implement Phase 1.4 backend REST API`
- `docs(release): add Phase 1 release engineering assets`
- `test(recommendation): add multi-attribute scorer unit tests`

---

## 4. Development & Testing Requirements

Before submitting a Pull Request, ensure that all tests pass:

```bash
# Run all unit, integration, and smoke tests
make test
make smoke

# Validate datasets
make validate
```

---

## 5. Pull Request Workflow

1. Push your working branch to GitHub:
   ```bash
   git push origin feature/your-branch-name
   ```
2. Open a Pull Request targeting the `main` branch.
3. Ensure GitHub Actions CI checks pass.
4. Request code review from repository maintainers before merging.
