PROJECT_NAME = os.getenv('PROJECT_NAME')
PROJECT_ENVIRONMENT_TYPE = os.getenv('PROJECT_ENVIRONMENT_TYPE')

access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" "{}" "{}"'.format(
    PROJECT_NAME,
    PROJECT_ENVIRONMENT_TYPE
)

# ============================================

#export GUNICORN_CMD_ARGS="--bind=0.0.0.0:5000 \
#           --access-logfile=./logs/access.log \
#             --error-logfile=./logs/app.log \
#--access-logformat='%(t)s %(l)s %({HOSTNAME}e)s %(l)s %({X-Forwarded-For}i)s %(l)s %(r)s %(s)s %(b)s %(f)s %(a)s'"


