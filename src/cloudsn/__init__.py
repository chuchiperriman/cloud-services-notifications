import logging, tempfile

LOGGING_FILE=tempfile.gettempdir() + '/cloudsn.log'

logging.basicConfig(filename=LOGGING_FILE,level=logging.DEBUG)

logger = logging.getLogger(__name__)

logger.info('Cloudsn initialized')
