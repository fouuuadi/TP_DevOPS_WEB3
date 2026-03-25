# Module metier pour la gestion de citations
# Store en memoire avec un dict -- en prod on brancherait sur PostgreSQL

import uuid
from datetime import datetime, timezone


_quotes = {}


def _seed_defaults():
    """Pre-remplit quelques citations pour pas demarrer avec une API vide."""
    defaults = [
        {"author": "Linus Torvalds", "text": "Talk is cheap. Show me the code."},
        {"author": "Grace Hopper", "text": "The most dangerous phrase is: We have always done it this way."},
        {"author": "Kent Beck", "text": "Make it work, make it right, make it fast."},
    ]
    for q in defaults:
        add_quote(q["author"], q["text"])


def list_quotes():
    """Renvoie toutes les citations sous forme de liste."""
    return list(_quotes.values())


def get_quote(quote_id):
    """Renvoie une citation par son ID, ou None si introuvable."""
    return _quotes.get(quote_id)


def add_quote(author, text):
    """Cree une nouvelle citation avec un UUID et un timestamp."""
    quote_id = str(uuid.uuid4())
    quote = {
        "id": quote_id,
        "author": author,
        "text": text,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    _quotes[quote_id] = quote
    return quote


def delete_quote(quote_id):
    """Supprime une citation. Renvoie True si elle existait, False sinon."""
    return _quotes.pop(quote_id, None) is not None


def count_quotes():
    """Nombre total de citations en memoire."""
    return len(_quotes)


def clear_quotes():
    """Vide le store -- utile pour les tests."""
    _quotes.clear()
