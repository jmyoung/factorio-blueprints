#
# Reads in a blueprint book, and splits it into its component blueprints.
#

import base64
import zlib
import json
import argparse

# An encoded blob, may be either a book or a blueprint
# You don't usually instantiate this.
class EncodedBlob:
    def __init__(self, label):
        self.versionCode = '0'
        self.label = label
        self.version = 73018245120
        
    # Decode a file, returning either a BlueprintBook or a Blueprint
    @staticmethod
    def decode_from_file(filename):
        f = open(filename,"r")
        blob = EncodedBlob.decode_from_string(f.read())
        f.close()
        return blob

    # Decode a string
    @staticmethod
    def decode_from_string(content):
        # All books/blueprints start with the character '0', which we will strip.
        # Base64 decode the resulting content
        # Decompress the stream, resulting in a JSON object
        encoded = content[1:]
        compressed = base64.b64decode(encoded)
        blob = json.loads(zlib.decompress(compressed))
            
        # Return the right kind of new object.
        if 'blueprint' in blob:
            return Blueprint.from_json(blob)
        elif 'blueprint_book' in blob:
            return BlueprintBook.from_json(blob)
            
        
# A blueprint book, containing zero or more blueprints
class BlueprintBook(EncodedBlob):
    def __init__(self, label="Blueprint Book"):
        self.active_index = 0
        self.blueprints = {}
        self.item = 'blueprint-book'
        EncodedBlob.__init__(self,label)

    # Populate this blueprint with the passed in JSON from an encoded blob
    @staticmethod
    def from_json(data):
        # Find the inner data structure
        inner = data
        if 'blueprint_book' in data:
            inner = data['blueprint_book']

        # Create a new BlueprintBook object
        book = BlueprintBook(inner['label'])
        book.version = inner['version']
        book.active_index = inner['active_index']

        # If there are blueprints, walk through them
        for bp in inner['blueprints']:
            book.blueprints[bp['index']] = Blueprint.from_json(bp['blueprint'])

        return book

    # Encode this blueprint as a shareable string
    def to_json(self):
        output = { 
            'blueprint_book': {
                'label': self.label,
                'item': self.item,
                'version': self.version,
                'active_index': self.active_index,
                'blueprints': []
            }
        }

        # JSON-ify each blueprint and add it to the output
        for index in sorted(self.blueprints.keys()):
            bpjson = self.blueprints[index].to_json()
            bpjson['index'] = index
            output['blueprint_book']['blueprints'].append(bpjson)

        return output

    # Encode this blueprint book as a blob
    def encode(self):
        # Get the JSON representation of this object
        output = self.to_json()
        
        # Compress the stream and base64 encode it
        b64 = base64.b64encode(zlib.compress(bytearray(json.dumps(output),'utf-8')))

        # Append a "0" string and return it
        return f'0{b64.decode("utf-8")}'



# A single blueprint
class Blueprint(EncodedBlob):
    def __init__(self, label="Blueprint"):
        self.icons = []
        self.entities = []
        self.tiles = []
        self.item = 'blueprint'
        EncodedBlob.__init__(self,label)

    def __str__(self):
        return self.label

    # Populate this blueprint with the passed in JSON from an encoded blob
    @staticmethod
    def from_json(data):
        # Find the inner data structure
        inner = data
        if 'blueprint' in data:
            inner = data['blueprint']
        
        # Create a new Blueprint object
        bp = Blueprint(inner['label'])
        bp.version = inner['version']
        bp.icons = inner['icons'] if 'icons' in inner else None
        bp.entities = inner['entities'] if 'entities' in inner else None
        bp.tiles = inner['tiles'] if 'tiles' in inner else None

        return bp

    # Return this blueprint as an encodable JSON object
    def to_json(self):
        output = { 
            'blueprint': {
                'label': self.label,
                'item': self.item,
                'version': self.version
            }
        }

        if self.icons is not None:
            output['blueprint']['icons'] = self.icons
        if self.entities is not None:
            output['blueprint']['entities'] = self.entities 
        if self.tiles is not None:
            output['blueprint']['tiles'] = self.tiles

        return output

    # Encode this blueprint as a standalone, single blueprint blob
    def encode(self):
        # Get the JSON representation of this object
        output = self.to_json(self)
        
        # Compress the stream and base64 encode it
        b64 = base64.b64encode(zlib.compress(bytearray(json.dumps(output),'utf-8')))

        # Append a "0" string and return it
        return f'0{b64.decode("utf-8")}'

# ----------------------------------------------

if __name__ == "__main__":
    #blob = EncodedBlob.decode_from_file("print.txt")
    #print(blob)
    #print(blob.encode())

    content = open("book.txt","r").read()
    blob = EncodedBlob.decode_from_string(content)
    
    