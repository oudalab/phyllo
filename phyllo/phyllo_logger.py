

import logging

# home_dir = os.path.expanduser('~/phyllo_data')
# log_path = os.path.join(home_dir, 'phyllo.log')


logger = logging.getLogger("phyllo")  # pylint: disable=invalid-name
logger.setLevel(logging.INFO)

# ch = logging.FileHandler(log_path)
ch = logging.StreamHandler()  # pylint: disable=invalid-name
ch.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s %(levelname)s:%(name)s %(message)s")  # pylint: disable=line-too-long,invalid-name

ch.setFormatter(formatter)

logger.addHandler(ch)
logger.info("Now logging")
