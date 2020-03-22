base = {
    "version": 1,
    "formatters": {
        'detailed': {
            'class': 'logging.Formatter',
            'format': '%(asctime)s %(levelname)-8s %(message)s', 
            'datefmt': "%H:%M:%S"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "detailed",
            # "stream": "ext://sys.stdout"
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

# End File: lan-nanny/lan_nanny/config/logging_conf.py