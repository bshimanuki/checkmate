After everything is set up, use the following to build the components and start the server.

You will need credentials in Discord and in Drive.
Drive:
1. Create or select a project [here](https://console.developers.google.com/).
1.
[Enable the Drive API Instructions.](https://developers.google.com/drive/api/v3/enable-drive-api)
1. Do the same for the Sheets API.
1. [Create a service account.](https://console.cloud.google.com/iam-admin/serviceaccounts)
1. Create a key and download the json to `credentials`. Rename or add the filename to `SECRETS.yaml`.

Ensure the database is setup:
```
docker-compose build
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
docker exec checkmate_app_1 app/backend/manage.py makemigrations checkmate accounts puzzles
docker exec checkmate_app_1 app/backend/manage.py migrate
docker exec checkmate_app_1 app/backend/manage.py shell -c "from django.contrib.auth.models import User; User.objects.create_superuser('admin', password='admin')"
docker-compose down
```

To run in `dev` mode, run the following:
```
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
docker restart checkmate_app_1
```

To run in `prod` mode, run the following (replace `docker-compose.prod.yml` with `docker-compose.prod.localhost.yml` if running locally):
```
set -e
rm -rf frontent/build || true
docker exec checkmate_app_1 yarn --cwd app/frontend build
rm -rf backend/build || true
docker exec checkmate_app_1 app/backend/manage.py collectstatic
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
docker restart checkmate_app_1
```
