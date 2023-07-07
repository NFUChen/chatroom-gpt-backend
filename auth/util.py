import random
import string

def generate_unique_random_string(string_len: int = 50) -> str:
    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choice(characters) for _ in range(string_len))
    return random_string