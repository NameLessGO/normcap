"""Find new version on github or pypi."""
import logging
from urllib.request import urlopen

from PySide6 import QtCore

logger = logging.getLogger(__name__)


class Communicate(QtCore.QObject):
    """TrayMenus' communication bus."""

    on_download_finished = QtCore.Signal(str)
    on_download_failed = QtCore.Signal()


class Downloader(QtCore.QObject):
    """Downloader using QNetworkAccessManager.

    It is async (provides signal) and avoids an issue on macOS, where the import
    of urllib.request fails with 'no module named _scproxy' in the packaged version.
    """

    def __init__(self):
        super().__init__()
        self.com = Communicate()

    def get(self, url: str):
        """Start downloading url. Emits signal, when done."""
        logger.debug("Download %s", url)
        if not url.lower().startswith("http"):
            raise ValueError(f"Url {url} not allowed to be opened")
        try:
            with urlopen(url) as response:  # nosec B310 # Validated above
                raw_data = response.read()
                data = raw_data.decode("utf-8", "ignore")
                self.com.on_download_finished.emit(data)
        except Exception as e:  # pylint: disable=broad-except
            logger.error("Download failed due to %s", e)
            self.com.on_download_failed.emit()
