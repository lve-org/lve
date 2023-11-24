from generator.site import LVESiteGenerator
import os
import shutil
import time
import datetime
from indexer import LVEIndex

if __name__ == '__main__':
    os.makedirs("new-build", exist_ok=True)

    # get build hash and time
    build_hash = "local"
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
    if os.path.isdir(os.path.join(PROJECT_ROOT, ".git")):
        # check for dirty working tree
        if os.environ.get("HOT") == "1":
            build_hash = "dev"
        else:
            build_hash = os.popen("git rev-parse --short HEAD").read().strip()
    
    # international non-ambiguous date format
    build_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    index = LVEIndex()
    index.build()

    generator = LVESiteGenerator(target="new-build")
    generator.build(index=index, build_hash=build_hash, build_time=build_time)

    # move new-build/ build/ for more seamless live reload
    shutil.copytree("new-build/", "build/", dirs_exist_ok=True)
    print("[" + time.strftime("%H:%M:%S") + "] Build complete")