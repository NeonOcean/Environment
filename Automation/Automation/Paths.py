import os
import platform
import re
import typing
from json import decoder

from Automation.Tools import Registry

def GetExcludedEnvironmentPaths () -> typing.List[str]:
	return [
		ModsPath,
		SitesPath
	]

def _GetS4UserDataPath () -> str:
	if platform.system() == "Windows":
		import winreg

		pathPrefix = Registry.ReadRegistry(winreg.HKEY_CURRENT_USER, "Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\User Shell Folders", "Personal")  # type: str

		# noinspection SpellCheckingInspection
		if pathPrefix.lower().startswith("%userprofile%"):
			# noinspection SpellCheckingInspection
			pathPrefix = re.sub(re.escape("%userprofile%"), re.escape(os.getenv("UserProfile")), pathPrefix, count = 1, flags = re.IGNORECASE)
	else:
		pathPrefix = os.path.join(os.path.expanduser('~'), "Documents")

	return os.path.join(os.path.normpath(pathPrefix), "Electronic Arts", "The Sims 4")

def _SetupExternalPaths () -> None:
	global ExternalPath

	with open(os.path.join(AutomationPath, "External.json")) as externalFile:
		externalInformation = decoder.JSONDecoder().decode(externalFile.read())
		externalRelativePath = externalInformation["External Path"]  # type: str

		ExternalPath = os.path.normpath(os.path.abspath(os.path.join(AutomationPath, externalRelativePath)))

S4UserDataPath = _GetS4UserDataPath()  # type: str
S4ModsPath = os.path.join(S4UserDataPath, "Mods")  # type: str

AutomationPath = os.path.dirname(os.path.dirname(os.path.normpath(__file__)))  # type: str
STBLCollisionsPath = os.path.join(AutomationPath, "STBL Collisions")  # type: str
RootPath = os.path.dirname(AutomationPath)  # type: str

ApplicationPath = os.path.join(RootPath, "Applications")  # type: str

ModsPath = os.path.join(RootPath, "Mods")  # type: str
SitesPath = os.path.join(RootPath, "Websites")

PublishingPath = os.path.join(RootPath, "Publishing")  # type: str

ExternalPath = None  # type: str

_SetupExternalPaths()

DistributionPath = os.path.join(ExternalPath, "Distribution")  # type: str

DistributionReleasesPath = os.path.join(DistributionPath, "Releases")  # type: str
DistributionPreviewsPath = os.path.join(DistributionPath, "Previews")  # type: str

WebsitesHostingPath = os.path.join(ExternalPath, "Websites")  # type: str
