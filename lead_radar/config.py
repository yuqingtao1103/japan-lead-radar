"""Read secrets without ever printing their values."""

import os

import streamlit as st


def get_secret(name: str) -> str | None:
    """Return a secret from Streamlit secrets or the environment, or None if missing."""
    try:
        value = st.secrets.get(name)
    except (FileNotFoundError, st.errors.StreamlitSecretNotFoundError):
        value = None
    if not value:
        value = os.environ.get(name)
    return value or None


def has_secret(name: str) -> bool:
    return get_secret(name) is not None
