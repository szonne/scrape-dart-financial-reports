def get_api_key():
    try:
        auth = __import__('auth')
        return auth.API_KEY
    except ModuleNotFoundError:
        return None
