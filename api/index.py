"""Vercel serverless entry point (WSGI).

Vercel's Python runtime imports this module and calls the `app` object.
The project root is not guaranteed to be on sys.path, so it is added
explicitly before importing the Flask application.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app import app  # noqa: E402  (the Flask WSGI application)

# Older Vercel runtimes look for `handler`; newer ones use `app`.
handler = app