import sys
import logging as l 
from google.appengine.api import memcache

class Validators:
  def make_option_list(self, name, list_op, default=0, ns='root', special_values=[]):
    def validator(self, value):
      for sv in special_values:
        if value == sv[0]: return sv[1]
      r = value
      if not value or not value in list_op: r = list_op[default]
      return r
    setattr(self, ns+'_'+name, validator)
    
  def make_max_min(self, name, value_type, minimum, maximum, default, ns='root', special_values=[]):
    def validator(self, value):
      for sv in special_values:
        if value == sv[0]: return sv[1]
      r = default
      if value:
        try: 
          r = value_type(value)
          if r > maximum or r < minimum: r = default
        except ValueError: pass
      return r
    setattr(self, ns+'_'+name, validator)
    
  def make_memcache(self, name, memcache_ns, ns='root'):
    def validator(self, value):
      r = memcache.get(memcache_ns + '.' + value)
      if not r:
        #l.error('%s.%s alias not present: %s' % (memcache_ns, name, value)) 
        raise ValidationError('%s.%s alias not present: %s' % (memcache_ns, name, value))
      return r
    setattr(self, ns+'_'+name, validator)

class ValidationError(Exception):
  pass
    
