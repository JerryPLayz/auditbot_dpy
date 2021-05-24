try:
    import cPickle as pickle
except ModuleNotFoundError:
    import pickle
import os, sys
def write_pickle_obj(filename, obj):
    with open(f"saves/{filename}.pkl", 'wb') as output:
        pickle.dump(obj, filename, -1)

def get_pickle_obj(filename):
    try:
        with open(f"saves/{filename}.pkl", 'rb') as inp:
            obj = pickle.load(inp)
            return obj
    except BaseException:
        return None

def del_pickle_obj(filename):
    try:
        os.remove(f"saves/{filename}.pkl")
        return True
    except BaseException as BE:
        exc = sys.exc_info()
        print(f"{exc[0]}\n==> {exc[1]}\n==>{exc[2]}\n====================\n")
        return False
        

        
