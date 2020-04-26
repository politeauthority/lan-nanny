base = {
    "version": 1,
    "formatters": {
        'detailed': {
            'class': 'logging.Formatter',
            'format': '%(asctime)s %(name)-10s %(levelname)-8s %(processName)-15s %(message)s'
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "detailed",
        },
    },
    "root": {
        "level": "INFO",
        "handlers": ["console"]
    },
    "s3transfer": {
        "level": "CRITICAL",
        "handlers": ["console"],
    },
    "boto3core": {
        "level": "CRITICAL",
        "handlers": ["console"],
    },
}

# End File: packagehistory/src/modules/logging_conf.py