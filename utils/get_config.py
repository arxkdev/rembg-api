from os import getenv

# Load environment variables
def load_config():
    config = {
        'admin_token': getenv('ADMIN_TOKEN'),
        'allowed_tokens': getenv('ALLOWED_TOKENS').split(','),
        # 0 or 1 (0 is False, 1 is True)
        'debug': getenv('DEBUG') == '1',
    }
    return config