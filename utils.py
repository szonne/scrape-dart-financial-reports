from datetime import date

def get_api_key():
    try:
        auth = __import__("auth")
        return auth.API_KEY
    except ModuleNotFoundError:
        return None


def get_age(birth_year: int, birth_month: int):
    today = date.today()
    return today.year - birth_year - ((today.month, today.day) < (birth_month, 1))


def remove_escape_characters(input_string:str) -> str:
    """
    Remove escape characters from a string.

    Parameters:
    input_string (str): The string from which escape characters will be removed.

    Returns:
    str: The string with escape characters removed.
    """
    escape_characters = ['\n', '\t', '\r', '\b', '\f', '\v', '\xa0']

    # Replace escape characters with an empty string
    for char in escape_characters:
        input_string = input_string.replace(char, '')

    return input_string
