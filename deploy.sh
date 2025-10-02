#!/bin/bash
set -e
set -a
source .env
set +a

PROJECT_DIR="/opt/star-burger"
cd "$PROJECT_DIR"
BRANCH="master"
LOCAL_USERNAME=$(whoami)

echo "=== Deploy: pulling latest changes ==="

git fetch origin "$BRANCH"
git pull origin "$BRANCH" --rebase --autostash --quiet

source "$PROJECT_DIR/.venv/bin/activate"
pip install --no-input --quiet -r requirements.txt

npm ci --omit=dev --quiet
./node_modules/.bin/parcel build bundles-src/index.js --dist-dir bundles --public-url="./"

python manage.py makemigrations --dry-run --check
python manage.py migrate --noinput
python manage.py collectstatic --noinput

sudo systemctl restart star-burger

curl https://api.rollbar.com/api/1/deploy/ \
  -F access_token=$ROLLBAR_TOKEN \
  -F environment=$ROLLBAR_ENVIRONMENT \
  -F revision=$(git rev-parse --short HEAD) \
  -F local_username=$LOCAL_USERNAME

echo "=== Deploy successfully finished! ==="
