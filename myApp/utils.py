import hashlib
import json



def ingredients_hash(ingredients):
    """Take list of ingredients and return a hash string."""
    return hashlib.sha256(json.dumps(ingredients, sort_keys=True).encode()).hexdigest()