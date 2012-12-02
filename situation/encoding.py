from __future__ import unicode_literals
import json
from datetime import datetime

from google.appengine.ext import db


SIMPLE_TYPES = (int, long, float, bool, dict, basestring, list, datetime)
_ERROR_MSG = 'Object of type {0} with value of {1} is not JSON serializable'


class JSONSterlingSerializer(object):

    def __init__(self, explicit_none_check=False):
        self.serialization_chain = []
        self.explicit_none_check = explicit_none_check

    def add(self, callable_serializer):
        self.serialization_chain.append(callable_serializer)
        return self

    def __call__(self, serializable):
        for serializer in self.serialization_chain:
            result = serializer(serializable)
            if ((not self.explicit_none_check and result) or
                (self.explicit_none_check and result is not None)):
                return result

        error_msg = _ERROR_MSG.format(type(serializable), repr(serializable))
        raise TypeError(error_msg)


def handle_datetime(serializable):
    if hasattr(serializable, 'isoformat'):
        # Serialize DateTime objects to RFC3339 protocol.
        # http://www.ietf.org/rfc/rfc3339.txt
        return serializable.isoformat() + 'Z'


# should be a singleton
default_json_serializer = JSONSterlingSerializer()
default_json_serializer.add(handle_datetime)


def to_json(*args, **kwargs):

    is_xhr = kwargs.pop('is_xhr', None)
    indent = None if is_xhr else 2
    return json.dumps(dict(*args, **kwargs),
                      indent=indent,
                      default=default_json_serializer)


def to_dict(model):
    output = {}

    for key, prop in model.properties().iteritems():
        value = getattr(model, key)

        if value is None or isinstance(value, SIMPLE_TYPES):
            output[key] = value
        elif isinstance(value, db.Model):
            output[key] = to_dict(value)
        else:
            raise ValueError('cannot encode ' + repr(prop))


    return output
