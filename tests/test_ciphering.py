import ciphering

def test_hash():
    password_hash = ciphering.get_password_hash('atata')
    assert password_hash == b'Z\xf9\xec\xd6\xdd\xe3\x88#\x00\x86\x08\x9d\x06\xc7\x9a\xfd'

