from config import config

def Authenticate(x_api_key):
    if x_api_key in config["allowed_tokens"]:
        return "allowed"
    elif x_api_key == config["admin_token"]:
        return "admin"
    else:
        return False