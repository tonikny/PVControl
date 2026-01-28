import pickle
import sys

f = open(sys.argv[1], 'rb')   # 'rb' for reading binary file
mydict = pickle.load(f)
f.close()

print(mydict)
