# Auto Parts Search Engine (FTS5 & Faceted Search)

A high-performance search API built with FastAPI and SQLite FTS5. It provides full-text search capabilities combined with dynamic faceted filtering via JSON attributes, simulating an ElasticSearch-like experience in a lightweight relational database.

## Features
- **Full-Text Search (FTS5)**: Fast text matching and relevance ranking for product titles and descriptions.
- **Dynamic Faceted Search**: Extracts and filters by dynamic JSON attributes (e.g., `diametru_mm`, `soclu`, `putere_W`) without requiring rigid schema changes.
- **Auto-Generating Filters**: Automatically returns available dynamic filters based on the current search results.
- **FastAPI Backend**: Modern, fast web framework with automatic interactive API documentation.

## Prerequisites
- Python 3.x
- `fastapi`
- `uvicorn`
- `pydantic`

## Usage
Run the local server:
```bash
uvicorn elastic_search:app --reload