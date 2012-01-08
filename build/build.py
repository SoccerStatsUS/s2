import shutil

from load import load
from generate import generate

from s2.utils import timer

@timer
def build():
    shutil.copy('/home/chris/www/s2/db/soccer.template.db', 
                '/home/chris/www/s2/db/soccer.build.db')

    load()
    generate()

    shutil.copy('/home/chris/www/s2/db/soccer.db', 
                '/home/chris/www/s2/db/soccer.backup.db')

    shutil.copy('/home/chris/www/s2/db/soccer.build.db', 
                '/home/chris/www/s2/db/soccer.db')

        


if __name__ == "__main__":
    load()
        
