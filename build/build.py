import shutil

from load import load
from generate import generate

from utils import timer

from settings import PROJECT_DIR

@timer
def build():
    shutil.copy('%s/db/soccer.template.db' % PROJECT_DIR, 
                '%s/db/soccer.build.db' % PROJECT_DIR)

    load()
    generate()

    shutil.copy('%s/db/soccer.db' % PROJECT_DIR, 
                '%s/db/soccer.backup.db' % PROJECT_DIR)

    shutil.copy('%s/db/soccer.build.db' % PROJECT_DIR, 
                '%s/db/soccer.db' % PROJECT_DIR)

        


if __name__ == "__main__":
    load()
        
