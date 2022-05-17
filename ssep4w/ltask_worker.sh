#celery --app=worker:app worker
cwd=$(pwd)
cd ..
cd ..
pwd
celery -A apps.ssep4w.ltask_worker worker -l info
cd $cwd
