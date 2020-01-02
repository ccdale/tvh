import logging
import logging.handlers


def setDebug():
    log.setLevel(logging.DEBUG)


def setInfo():
    log.setLevel(logging.INFO)


def main():
    log.info("logging is working")


logging.basicConfig(format="%(asctime)s %(message)s", datefmt="%d/%m/%Y %H:%M:%S")
log = logging.getLogger(__name__)
setInfo()

if __name__ == "__main__":
    main()
