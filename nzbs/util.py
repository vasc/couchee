import time

class UnavailableError(Exception):
    pass

def retry(ExceptionToCheck, tries=4, delay=3, backoff=2, silent_fail=False):
    """Retry decorator
    original from http://wiki.python.org/moin/PythonDecoratorLibrary#Retry
    """
    def deco_retry(f):
        def f_retry(*args, **kwargs):
            mtries, mdelay = tries, delay
            try_one_last_time = not silent_fail
            if silent_fail: mtries+=1
            while mtries > 1:
                try:
                    return f(*args, **kwargs)
                    #try_one_last_time = False
                    #break
                except ExceptionToCheck, e:
                    print "%s, Retrying in %d seconds..." % (str(e), mdelay)
                    time.sleep(mdelay)
                    mtries -= 1
                    mdelay *= backoff
            if try_one_last_time:
                return f(*args, **kwargs)
            return None
        return f_retry # true decorator
    return deco_retry
    
class Memcached():
    m = None
    h = {}
    size = 0

    def __init__(self, max_bytes = 40000):
        self.mm = max_bytes / 2
        
    def setkey(self, key, data):
        self.h[key] = data;
        
    def getkey(self, key):
        return self.h[key]
        
    def testkey(self, key):
        return key in self.h
        
        
