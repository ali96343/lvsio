#celery --app=worker:app worker
cwd=$(pwd)
cd ..
cd ..
pwd
celery -A apps.flvsiossl.worker worker -l info
cd $cwd
