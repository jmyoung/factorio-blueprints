#
# Reads in a blueprint book, and splits it into its component blueprints.
# blueprintSchema.json taken from https://github.com/Teoxoy/factorio-blueprint-editor
#

import sys
import argparse
import base64
import zlib
import json

import jsonschema

# An encoded blob, may be either a book or a blueprint
# You don't usually instantiate this.
class EncodedBlob:
    def __init__(self, label):
        self.versionCode = '0'
        self.label = label
        self.version = 73018245120
        
    # Decode a string and return the raw json blob
    @staticmethod
    def decode_to_json(content):
        # All books/blueprints start with the character '0', which we will strip.
        # Base64 decode the resulting content
        # Decompress the stream, resulting in a JSON object
        encoded = content[1:]
        compressed = base64.b64decode(encoded)
        blob = json.loads(zlib.decompress(compressed))
        return blob

    # Take a raw json blob and convert it into an object            
    @staticmethod
    def json_to_object(raw):
        # Return the right kind of new object.
        if 'blueprint' in raw:
            return Blueprint.from_json(raw)
        elif 'blueprint_book' in raw:
            return BlueprintBook.from_json(raw)

    @staticmethod
    def decode(content):
        return EncodedBlob.json_to_object(EncodedBlob.decode_to_json(content))

    # Take a raw json blob and encode it into a blob
    @staticmethod
    def encode_blob(content):
        b64 = base64.b64encode(zlib.compress(bytearray(json.dumps(content),'utf-8')))

        # Append a "0" string and return it
        return f'0{b64.decode("utf-8")}'

            
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
        book = BlueprintBook(inner['label'] if 'label' in inner else 'Blueprint Book')
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

        # Encode it
        return EncodedBlob.encode_blob(output)


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
        bp = Blueprint(inner['label'] if 'label' in inner else 'Blueprint')
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
        output = self.to_json()
                
        # Encode it
        return EncodedBlob.encode_blob(output)

# ----------------------------------------------

if __name__ == "__main__":
    
    # Read in the wired book
    wired = EncodedBlob.decode(open("wired.txt","r").read())

    # Read in the nowires book
    nowires = EncodedBlob.decode(open("nowires.txt","r").read())

    # Read in a BP with just four electric poles in it
    bp = EncodedBlob.decode('0eJydkcEKwjAQRP9lzqkY2yrm6G+ISFsXWUjTkqRiKf13kyrqRbTedpeZN7AzoNQdtZaNhxrAVWMc1H6A47MpdLz5viUosKcaAqao41byOSFNlbdcJW2jCaMAmxNdoeR4ECDj2TPdYR9NAm3jgq4xMSl4E5ktcoH+MQXoiW1wTIrlA9sfTVeXZGOUmEOX6Rz46k94HL6x03ns11t+gWexgKkv9VavwIWsmyybdCnzdC1zuRXQRUmhaOyeynG8AUTOrjE=')

    
    # For each pole, try and link it up with red/green wires
    for entity in bp.entities:
        # We only care about big electric poles
        if entity['name'] != 'big-electric-pole':
            continue

        # If the pole has no connections...
        if 'connections' not in entity:
            # Add a connection for every pole
            conns = {}
            iter = 1
            for targetpole in bp.entities:
                if targetpole['name'] != 'big-electric-pole' or targetpole['entity_number'] == entity['entity_number']:
                    continue
                else:
                    conns[str(iter)] = {"red": [{"entity_id": targetpole['entity_number']}], "green": [{"entity_id": targetpole['entity_number']}]}
                    iter = iter+1
            
            # Insert that into the pole object
            entity['connections'] = conns

            # Remove the direction if it exists
            if 'direction' in entity:
                entity.pop('direction')


    sys.stdout.write(bp.encode())
    print("Done")
    

    
    