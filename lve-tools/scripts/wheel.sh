# fail if any commands fails
set -e

COMMIT=$(git rev-parse HEAD)
HAS_UNSTAGED=$(git diff-index --quiet HEAD -- src; echo $?)

if [ $HAS_UNSTAGED -eq 1 ]; then
    echo "Unstaged changes detected. Please commit or stash them before packaging for PyPI."
    echo $(git diff-index HEAD -- src)
    exit 1
fi

VERSION=$1
VERSION_BEFORE=$(cat lve-tools/lve/version.py)
echo "version = \"$VERSION\"" > lve-tools/lve/version.py
echo "commit = \"$COMMIT\"" >> lve-tools/lve/version.py
echo "build_on = \"$(date)\"" >> lve-tools/lve/version.py

echo "Building with version information: $(cat lve-tools/lve/version.py)"

# replace line starting 'version = ' in setup.cfg
UPDATED_SETUP=$(sed "s/version = .*/version = $VERSION/" setup.cfg)
echo "$UPDATED_SETUP" > setup.cfg

# run and ignore failure
python -m build

echo "Reverting version.py to dev"
git checkout HEAD lve-tools/lve/version.py