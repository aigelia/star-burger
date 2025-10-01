#!/bin/bash
set -e

PROJECT_DIR="/opt/star-burger"
BRANCH="master"

echo "=== Deploy: pulling latest changes ==="
cd "$PROJECT_DIR"

git fetch origin "$BRANCH"
git reset --hard "origin/$BRANCH"
source "$PROJECT_DIR/.venv/bin/activate"
pip install -r requirements.txt

./node_modules/.bin/parcel build bundles-src/index.js --dist-dir bundles --public-url="./"

python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic || true

sudo systemctl restart star-burger
sudo systemctl start certbot-renewal.timer || true

echo "=== Deploy successfully finished! ==="
