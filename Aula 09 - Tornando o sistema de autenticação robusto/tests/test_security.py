from datetime import datetime
from zoneinfo import ZoneInfo

import jwt

from fast_zero.security import ALGORITHM, SECRET_KEY, create_access_token


def test_jwt():
    data = {'sub': 'test'}
    token = create_access_token(data)

    decoded_token = jwt.decode(jwt=token, key=SECRET_KEY, algorithms=ALGORITHM)

    print(decoded_token)

    assert decoded_token['sub'] == data['sub']
    assert 'exp' in decoded_token


def test_token_expiration():
    data = {'sub': 'test'}
    token = create_access_token(data)
    decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    assert 'exp' in decoded
    assert decoded['exp'] > datetime.now(tz=ZoneInfo('UTC')).timestamp()
