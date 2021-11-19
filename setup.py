import os
import shutil
from distutils import log
from distutils.command.install_scripts import install_scripts
from stat import ST_MODE
import sys
import tarfile
import urllib.request
from tempfile import TemporaryDirectory

from setuptools import setup

VERSION = "12.1.2"


def download_binary(path: str) -> str:
    if sys.platform == "win32":
        filename = "tokei-x86_64-pc-windows-msvc.exe"
    elif sys.platform == "linux":
        filename = "tokei-x86_64-unknown-linux-gnu.tar.gz"
    elif sys.platform == "darwin":
        filename = "tokei-x86_64-apple-darwin.tar.gz"
    else:
        raise OSError("Unsupported platform: {}".format(sys.platform))
    url = f"https://github.com/XAMPPRocky/tokei/releases/download/v{VERSION}/{filename}"
    log.info("Downloading binary from %s", url)
    if sys.platform == "win32":
        urllib.request.urlretrieve(url, os.path.join(path, "tokei.exe"))
        return os.path.join(path, "tokei.exe")
    else:
        urllib.request.urlretrieve(url, os.path.join(path, "tokei.tar.gz"))
        tarball = os.path.join(path, "tokei.tar.gz")
        with tarfile.open(tarball, "r:gz") as tar:
            tar.extractall(path)
        return os.path.join(path, "tokei")


class InstallTokei(install_scripts):
    def run(self):
        with TemporaryDirectory() as tmpdir:
            binary_path = download_binary(tmpdir)
            target_path = os.path.join(
                self.install_dir, "tokei.exe" if os.name == "nt" else "tokei"
            )
            os.makedirs(self.install_dir)
            log.info("Copying %s to %s", binary_path, target_path)
            if os.path.exists(target_path):
                os.remove(target_path)
            shutil.copy2(binary_path, target_path)
        if os.name == "posix":
            mode = ((os.stat(target_path)[ST_MODE]) | 0o555) & 0o7777
            os.chmod(target_path, mode)


setup(
    name="tokei",
    version=VERSION,
    cmdclass={"install_scripts": InstallTokei},
)
