# -*- coding: utf-8 -*-
import logging.config
import sys
from os import path


# log_file_path = path.join(path.dirname(path.abspath(__file__)), 'logging.ini')
# logging.config.fileConfig(log_file_path, disable_existing_loggers=False)

logger = logging.getLogger(__name__)
logger.info("running %s" % " ".join(sys.argv))
