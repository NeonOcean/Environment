import os

from Automation import Paths

def _GetS4Version () -> str:
	with open(os.path.join(Paths.S4UserDataPath, "GameVersion.txt"), "rb") as s4VersionFile:
		return s4VersionFile.read()[4:].decode("utf-8")

Version = _GetS4Version()  # type: str
