class AuthError(Exception):
    pass


class NotLoggedIn(AuthError):
    pass


class TokenExpired(AuthError):
    pass


class LoginError(AuthError):
    pass
