def check():
    """
    Checks if a user has an already authenticaed session
    :returns: Weather or not user is authenticated.
    :rtype: bool
    """
    if session.get('authenticated'):
        return True
    return False
