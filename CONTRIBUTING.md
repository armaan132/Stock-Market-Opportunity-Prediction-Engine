# Contributing

This project is organized like a small production data science system. Changes should keep the repository understandable to someone reviewing it later for architecture, modeling choices, and implementation quality.

## Development Workflow

1. Create or activate the local environment.

   ```bash
   make setup
   ```

2. Run the full training pipeline.

   ```bash
   make train
   ```

3. Verify code quality before committing.

   ```bash
   make test
   make lint
   ```

4. Keep generated data, databases, model binaries, and cache files out of git. The tracked `.gitkeep` files preserve directory structure while `.gitignore` excludes generated artifacts.

## Commit Style

Use clear, scoped commit messages:

```text
feat: add time-based model validation
docs: document raw data contract
test: cover feature engineering target creation
refactor: isolate storage layer
```

Prefer small commits that each explain one logical change. A reviewer should be able to read the history and understand how the project evolved: setup, pipeline, modeling, dashboard, tests, and documentation should not be mixed together unnecessarily.

## Pull Request Checklist

- The README still explains the project at a high level.
- `docs/ARCHITECTURE.md` is updated if the system design changes.
- `docs/DATA_CONTRACT.md` is updated if input or output columns change.
- `docs/MODELING.md` is updated if features, validation, or model choice changes.
- `make test` passes.
- `make lint` passes.
- No generated data or binary model artifacts are committed.
