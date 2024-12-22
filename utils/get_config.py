from os import getenv

# Load environment variables
def load_config():
    config = {
        'admin_token': getenv('ADMIN_TOKEN'),
        'allowed_tokens': getenv('ALLOWED_TOKENS').split(','),
    }
    return config