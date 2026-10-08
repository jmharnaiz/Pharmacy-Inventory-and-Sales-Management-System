from werkzeug.security import generate_password_hash, check_password_hash


def hash_password(plaintext):
    """Return a werkzeug scrypt hash for a plaintext password."""
    return generate_password_hash(plaintext)


def check_password(stored, plaintext):
    """Verify plaintext against a stored hash.

    Handles rows that somehow still hold plaintext (treat as equal) so a
    login never hard-fails during migration windows.
    """
    if not stored:
        return False
    if '$' not in stored:
        # Plaintext left behind by an older version of the app.
        return stored == plaintext
    return check_password_hash(stored, plaintext)