# Project Structure

The repository follows a standard Python `src/` layout with separate folders for the application, SQL schema, data, model artifacts, and tests.

```text
.
├── app/
│   └── streamlit_app.py
├── data/
│   ├── external/
│   ├── processed/
│   └── raw/
├── docs/
│   ├── ARCHITECTURE.md
│   ├── DATA_CONTRACT.md
│   ├── MODELING.md
│   └── PROJECT_STRUCTURE.md
├── models/
├── sql/
│   └── schema.sql
├── src/
│   └── market_opportunity/
├── tests/
├── CHANGELOG.md
├── CONTRIBUTING.md
├── Makefile
├── README.md
├── pyproject.toml
└── requirements.txt
```

## Tracked vs Generated Files

Tracked files include source code, tests, documentation, schema definitions, and empty `.gitkeep` placeholders.

Generated files are intentionally ignored:

- Raw demo CSVs
- Processed modeling frames
- SQLite databases
- Saved model binaries
- Python cache files
- Test and lint caches

This keeps git history readable while allowing anyone to regenerate artifacts with:

```bash
make train
```
