#celery --app=worker:app worker
cwd=$(pwd)
cd ..
cd ..
pwd
celery -A apps.flvsio.worker worker -l info
cd $cwd
