import base64
import zlib
import json
import pkgutil

import jsonschema

from . import Blueprint
from . import BlueprintBook

class EncodedBlob:
    """An EncodedBlob, with JSON content, representing various objects"""
    
    def __init__(self, blob=None):
        """Initializes a new EncodedBlob"""
        if blob is None:
            self.versionCode = '0'
            self.data = {}
        else:
            self.versionCode = blob[0]
            encoded = blob[1:]
            compressed = base64.b64decode(encoded)
            self.data = json.loads(zlib.decompress(compressed))

    def cast(self):
        """Returns a specific object type based on what kind this object is"""
        if self.validate():
            if 'blueprint' in self.data:
                # A single blueprint
                obj = Blueprint.Blueprint()
                obj.versionCode = self.versionCode
                obj.data = self.data
                return obj
            elif 'blueprint-book' in self.data:
                # A book of blueprints
                obj = BlueprintBook.BlueprintBook()
                obj.versionCode = self.versionCode
                obj.data = self.data
                return obj
            else:
                # Unknown datatype.  Just return the object
                return self
            
        else:
            # Broken validation means just return the object
            return self

    def validate(self) -> bool:
        """Validate that the JSON in the object matches an object definition"""

        # Start by reading in the blueprint schema json
        schema = json.loads(pkgutil.get_data("FactorioTools", "blueprintSchema.json"))

        # Validate the object's schema against the blueprintSchema JSON
        try:
            jsonschema.validate(self.data, schema)
            return True
        except jsonschema.ValidationError:
            pass

        return False

    def encode(self) -> str:
        """Take the current object and encode it""" 

        # Encode the object
        b64 = base64.b64encode(zlib.compress(bytearray(json.dumps(self.data,sort_keys=True),'utf-8')))

        # Append the version code string and return it
        return f'{self.versionCode}{b64.decode("utf-8")}'

    def __str__(self) -> str:
        """Casting a blob to a string returns the encoded version of it"""
        return self.encode()

    def __eq__(self, other) -> bool:
        """A blob is equal to another if the JSON is the same"""
        if json.dumps(self.data,sort_keys=True) == json.dumps(other.data,sort_keys=True):
            return True
        else:
            return False

    def __ne__(self, other) -> bool:
        """A blob is inequal to another if the JSON is different"""
        return not self.__eq__(other)

