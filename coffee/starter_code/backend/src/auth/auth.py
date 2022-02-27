import json
from lib2to3.pgen2 import token
from os import abort
from flask import request, _request_ctx_stack, jsonify, Flask
from functools import wraps
from jose import jwt
from urllib.request import urlopen


AUTH0_DOMAIN = 'dev-p7xsqvkb.us.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'https://coffee.com/api'

# AuthError Exception
'''

AuthError Exception
A standardized way to communicate auth failure modes
'''


class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


# Auth Header
'''
@TODO implement get_token_auth_header() method
    it should attempt to get the header from the request
        it should raise an AuthError if no header is present
    it should attempt to split bearer and the token
        it should raise an AuthError if the header is malformed
    return the token part of the header
'''


def get_token_auth_header():

    if 'Authorization' not in request.headers:
        raise AuthError({
            'code': 'authorization_header_missing',
            'description': 'Authorization header is expected.'
        }, 401)

    Gettig = request.headers['Authorization']
    authorizations = Gettig.split(" ")
    length = len(authorizations)

    if authorizations[0].lower() != 'bearer':
        raise AuthError({
            'code': 'Invalid_header',
            'description': 'Authorization header must start with bearer'
        }, 401)

    elif length == 1:
        raise AuthError({
            'code': 'Invalid_header',
            'description': 'Cannot found TOKEN'
        }, 401)

    elif length > 2:
        raise AuthError({
            'code': 'Invalid_header',
            'description': 'Authorization header should be bearer token'
        }, 401)

    return length[1]


'''
@TODO implement check_permissions(permission, payload) method
    @INPUTS
        permission: string permission (i.e. 'post:drink')
        payload: decoded jwt payload

    it should raise an AuthError if permissions are not included in the payload
        !!NOTE check your RBAC settings in Auth0
    it should raise an AuthError if the requested permission string is not in the payload permissions array
    return true otherwise
'''


def check_permissions(permission, payload):
    Boolean_value = True
    if 'permissions' not in payload:
        raise AuthError({
            'code': 'Invalid_claims',
            'description': 'No permission in token'
        }, 400)

    if permission not in payload['permissions']:
        abort(403)

    return Boolean_value


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
    Var = "https://"+AUTH0_DOMAIN+"/.well-known/jwks.json"
    JSON_Val = urlopen(Var)
    Loading = json.loads(JSON_Val.read())
    getHeader = jwt.get_unverified_header(token)

    if 'kid' not in getHeader:
        raise AuthError({
            'code': 'Invalid_header',
            'description': 'Authorization error'
        }, 401)

    List = {}

    for value in Loading['keys']:
        Key_val = value['kid']

        if Key_val == getHeader['kid']:
            List = {
                'kty': value['kty'], 'kid': value['kid'],
                'use': value['use'], 'n': value['n'],
                'e': value['e']
            }

    if List:
        try:
            Auth0 = "https://" + AUTH0_DOMAIN + "/"
            payload_decode = jwt.decode(
                token,
                List,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer=Auth0
            )

            return payload_decode

        except jwt.JWTClaimsError:
            raise AuthError({
                'code': 'Invalid_claims',
                'description': 'Invalid claims'
            }, 401)

        except jwt.ExpiredSignatureError:
            raise AuthError({
                'code': 'token_expired',
                'description': 'the Token is expired.'
            }, 401)

        except:
            raise AuthError({
                'code': 'Invalid_header',
                'description': 'Invalid header'
            }, 400)

    raise AuthError({
        'code': 'Invalid_header',
        'description': 'Cannot find key'
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
            return f(payload, *args, **kwargs)

        return wrapper
    return requires_auth_decorator
