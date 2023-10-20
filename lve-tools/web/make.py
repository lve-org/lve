from generator.main import LVESiteGenerator
import os
import shutil
import time

if __name__ == '__main__':
    os.makedirs("new-build", exist_ok=True)

    generator = LVESiteGenerator(target="new-build")
    generator.build()

    # move new-build/ build/ for more seamless live reload
    shutil.copytree("new-build/", "build/", dirs_exist_ok=True)
    print("[" + time.strftime("%H:%M:%S") + "] Build complete")