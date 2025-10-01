import os

# set config.env to "test" for pytest to prevent logging to file in utils.setup_logging()
os.environ["BASIC_MEMORY_ENV"] = "test"
