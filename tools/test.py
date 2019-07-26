from FactorioTools import *

if __name__ == "__main__":
    # Test 1:  Load up a pretty simple single blueprint
    bpdata = '0eJydkcEKwjAQRP9lzqkY2yrm6G+ISFsXWUjTkqRiKf13kyrqRbTedpeZN7AzoNQdtZaNhxrAVWMc1H6A47MpdLz5viUosKcaAqao41byOSFNlbdcJW2jCaMAmxNdoeR4ECDj2TPdYR9NAm3jgq4xMSl4E5ktcoH+MQXoiW1wTIrlA9sfTVeXZGOUmEOX6Rz46k94HL6x03ns11t+gWexgKkv9VavwIWsmyybdCnzdC1zuRXQRUmhaOyeynG8AUTOrjE='
    bp = EncodedBlob.EncodedBlob(bpdata)
    
    # Test 2: Cast it to a proper type
    obj = bp.cast()

