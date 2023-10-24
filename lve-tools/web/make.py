from generator.site import LVESiteGenerator
import os
import shutil
import time
from indexer import LVEIndex

if __name__ == '__main__':
    os.makedirs("new-build", exist_ok=True)

    index = LVEIndex()
    index.build()

    generator = LVESiteGenerator(target="new-build")
    generator.build(index=index)

    # move new-build/ build/ for more seamless live reload
    shutil.copytree("new-build/", "build/", dirs_exist_ok=True)
    print("[" + time.strftime("%H:%M:%S") + "] Build complete")