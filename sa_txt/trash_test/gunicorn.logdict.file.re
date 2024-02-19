{ 'logconf_dict' : {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'KeyValueFormatter': {
            'format': (
                'timestamp=%(asctime)s pid=%(process)d '
                'loglevel=%(levelname)s msg=%(message)s'
            )
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'KeyValueFormatter',
        },
         'logfile': {
            'level':'DEBUG',
            'class':'logging.FileHandler',
            'formatter': 'KeyValueFormatter',
            'filename': "FF",
        },


    },
    'loggers': {
        'gunicorn.access': {
            'propagate': True,
        },
        'gunicorn.error': {
            'propagate': True,
        },
    },
    'root': {
        'level': 'INFO',
        'handlers': ['console', 'logfile'],
    }
}
}
