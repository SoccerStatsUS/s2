from load import load
from generate import generate

from s2.utils import timer

@timer
def build():
    load()
    generate()

        


if __name__ == "__main__":
    load()
        
