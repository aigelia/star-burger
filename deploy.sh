#!/bin/bash
set -e

PROJECT_DIR="/opt/star-burger"
BRANCH="master"

echo "=== Deploy: pulling latest changes ==="
cd "$PROJECT_DIR"

git stash push -m "deploy backup" || true
git fetch origin "$BRANCH"
git pull origin "$BRANCH" --rebase
git stash pop || true

source "$PROJECT_DIR/.venv/bin/activate"
pip install -r requirements.txt

./node_modules/.bin/parcel build bundles-src/index.js --dist-dir bundles --public-url="./"

python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput

sudo systemctl restart star-burger
sudo systemctl start certbot-renewal.timer || true

echo "=== Deploy successfully finished! ==="
