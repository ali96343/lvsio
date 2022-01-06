#celery --app=worker:app worker
cd ..
cd ..
pwd
celery -A apps.flvsio.worker worker -l info

