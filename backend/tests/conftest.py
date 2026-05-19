"""
pytest configuration for backend/tests.

Both test files in this directory exercise PURE functions — no Flask
context, no DB, no I/O — so we don't need fixtures here yet. The file
exists so pytest treats `backend/` as the rootdir and finds tests
consistently across local + Docker runs.
"""
