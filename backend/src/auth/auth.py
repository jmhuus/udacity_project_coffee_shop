import json
from flask import request, _request_ctx_stack
from functools import wraps
from jose import jwt
from urllib.request import urlopen


AUTH0_DOMAIN = 'jordan-flask-authentication-practice.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'coffee_shop'

## AuthError Exception
'''
AuthError Exception
A standardized way to communicate auth failure modes
'''
class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


## Auth Header

'''
@TODO implement get_token_auth_header() method
    [COMPLETE] it should attempt to get the header from the request
        [COMPLETE] it should raise an AuthError if no header is present
    [COMPLETE] it should attempt to split bearer and the token
        [COMPLETE] it should raise an AuthError if the header is malformed
    [COMPLETE] return the token part of the header
'''
def get_token_auth_header():
    """
    Obtains the access token from the request's header.
    request > header > authorization > bearer & token

    Args:
        NONE: No parameters are required but this function relies on access
        to Flask's request object.

    Returns:
        JWT token string.

    Raises:
        KeyError: Raises an AuthError if the authorization header malformed or
        is missing.
    """
    auth = request.headers.get('Authorization', None)
    if not auth:
        raise AuthError({
            'code': 'authorization_header_missing',
            'description': 'Authorization header is expected.'
        }, 401)

    parts = auth.split()
    if parts[0].lower() != 'bearer':
        raise AuthError({
            'code': 'bearer_missing',
            'description': 'Authorization header must start with "Bearer".'
        }, 401)

    elif len(parts) == 1:
        raise AuthError({
            'code': 'token_missing',
            'description': 'Token not found.'
        }, 401)

    elif len(parts) > 2:
        raise AuthError({
            'code': 'inavlid_token',
            'description': 'Too many authorization headers.'
        }, 401)

    token = parts[1]
    return token


'''
@TODO implement check_permissions(permission, payload) method
    @INPUTS
        permission: string permission (i.e. 'post:drink')
        payload: decoded jwt payload

    [COMPLETE] it should raise an AuthError if permissions are not included in the payload
        [COMPLETE] !!NOTE check your RBAC settings in Auth0
    [COMPLETE] it should raise an AuthError if the requested permission string is not in the payload permissions array
    [COMPLETE] return true otherwise
'''
def check_permissions(permission, payload):
    """
    Checks if the requesting user is authorized to perform the action stated
    in the permission paramter.

    Args:
        permission: String value of the requesting permission; 'get:drinks'.
        payload: Dictionary of authorization data.

    Returns:
        True if the requesting permission is authorized.

    Raises:
        KeyError: Raises an AuthError.
    """
    if "permissions" not in payload:
        raise AuthError({
            'code': 'permissions_unavailable',
            'description': 'Permissions were not included in the payload.'
        }, 401)

    if permission not in payload["permissions"]:
        raise AuthError({
            'code': 'invalid_permission',
            'description': 'User does not have authorization; invalid permission provided.'
        }, 401)

    return True


'''
@TODO implement verify_decode_jwt(token) method
    @INPUTS
        token: a json web token (string)

    it should be an Auth0 token with key id (kid)
    it should verify the token using Auth0 /.well-known/jwks.json
    it should decode the payload from the token
    it should validate the claims
    return the decoded payload

    !!NOTE urlopen has a common certificate error described here: https://stackoverflow.com/questions/50236117/scraping-ssl-certificate-verify-failed-error-for-http-en-wikipedia-org
'''
def verify_decode_jwt(token):
    """
    Validates the user's JWT token and returns the contained payload. This
    function uses a public key (rsa_key) to verify the token's validity, which
    is retrieved from appending '/.well-known/jwks.json' to the domain.

    Args:
        token: String containing the JWT token.

    Returns:
        Payload contained in the JWT token IF the token is valid.

    Raises:
        KeyError: Raises an AuthError if the token is not valid.
    """

    # Retrieve token header
    unverified_header = jwt.get_unverified_header(token)
    rsa_key = {}
    if 'kid' not in unverified_header:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization malformed.'
        }, 401)

    # Retrieve public key (RSA key)
    jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json') # https://jordan-flask-authentication-practice.auth0.com/.well-known/jwks.json
    jwks = json.loads(jsonurl.read())
    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],     # Key type (i.e. RSA)
                'kid': key['kid'],     # Key ID (i.e. M0U5...)
                'use': key['use'],     # Use is to sign (i.e. sig) the token
                'n': key['n'],     # (i.e. u8ptXo...)
                'e': key['e']     # (i.e. AQAB)
            }

    # Decode using public key
    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer='https://' + AUTH0_DOMAIN + '/'
            )

            return payload

        except jwt.ExpiredSignatureError:
            raise AuthError({
                'code': 'token_expired',
                'description': 'Token expired.'
            }, 401)

        except jwt.JWTClaimsError:
            raise AuthError({
                'code': 'invalid_claims',
                'description': 'Incorrect claims. Please, check the audience and issuer.'
            }, 401)
        except Exception:
            raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to parse authentication token.'
            }, 400)
    raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to find the appropriate key.'
            }, 400)

'''
@TODO implement @requires_auth(permission) decorator method
    @INPUTS
        permission: string permission (i.e. 'post:drink')

    it should use the get_token_auth_header method to get the token
    it should use the verify_decode_jwt method to decode the jwt
    it should use the check_permissions method validate claims and check the requested permission
    return the decorator which passes the decoded payload to the decorated method
'''
def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            payload = verify_decode_jwt(token)
            check_permissions(permission, payload)
            return f(*args, **kwargs)

        return wrapper
    return requires_auth_decorator
