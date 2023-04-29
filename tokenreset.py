from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
def token(id,seconds):
    s=Serializer('*67@hjyjhk',seconds)
    return s.dumps({'user':id}).decode('utf-8')
