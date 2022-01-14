
def has_method(o, name):
    '''
    From: https://stackoverflow.com/questions/7580532/how-to-check-whether-a-method-exists-in-python
    :param o:
    :param name:
    :return:
    '''
    return callable(getattr(o, name, None))