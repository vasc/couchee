from validation import Validators
from google.appengine.api import memcache
import logging as l

def cache(f):
  '''Cache function results in memcache
  BE VERY WARY OF OBJECTS WITH GENERIC REPRESENTATION i.e. <object>
  '''
  db = {}
  
  def new_f(*args, **kwargs):
     key = ';'.join(map(repr, args) + ['%s=%s' % (repr(n), repr(kwargs[n])) for n in kwargs])
     r = memcache.get(key, namespace='function_cache')
     if r: 
        l.info('Hit: %s' % key)
        return r
     else:
        r = f(*args, **kwargs)
        memcache.set(key, r, namespace='function_cache')
        l.info('Miss: %s' % key)
        return r
  return new_f
     

def validate(ns='root'):
  validator = Validators()
  validator.make_option_list('order', ('age', 'name', 'imdbrating', 'imdbvotes'), ns='filter')
  validator.make_option_list('direction', ('ascending', 'descending'), default=1, ns='filter')
  
  validator.make_max_min('maxrating', float, 0.0, 10.0, 10.0, ns='filter')
  validator.make_max_min('minrating', float, 0.0, 10.0, 5.0, ns='filter')

  #() seems to be similar to infinity: () > 1E16 => True, however () > float('+inf') => True as well...
  validator.make_max_min('maxvotes', int, 0, (), (), ns='filter', special_values=[('()', ())])
  validator.make_max_min('minvotes', int, 0, (), 1000, ns='filter')

  validator.make_memcache('cursor', 'cursors', ns="filter")

  def wrap(f):
    parameters = f.func_code.co_varnames[1:]
    def new_f(self, *args, **kwargs):
      final = {}
      
      for i in range(0, len(args)):
        kwargs[parameters[i]] = args[i]
    
      param = [x for x in parameters if not x in kwargs]
        
      for p in param: kwargs[p] = self.request.get(p)
      for kw in kwargs:
        try:
          validation_method = getattr(validator, ns+'_'+kw)
          final[kw] = validation_method(validator, kwargs[kw])
          #l.debug('Validated %s: %s -> %s' % (kw, kwargs[kw], final[kw]))
        except Exception:
          e = None
          #l.error('Error validating %s: %s' % (kw, e))
          if kw not in param: final[kw] = kwargs[kw]
      #l.debug(final)
      return f(self, **final)
    return new_f
  return wrap
