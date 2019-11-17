import logging
import logging.handlers

logging.basicConfig(format="%(asctime)s %(message)s", datefmt="%d/%m/%Y %H:%M:%S")
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


def main():
    log.info("logging is working")


if __name__ == "__main__":
    main()
