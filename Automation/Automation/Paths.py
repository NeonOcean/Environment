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
	global DistributionReleasesPath, DistributionPreviewsPath, WebsitesDistributionPath

	with open(os.path.join(SettingsPath, "ExternalPaths.json")) as externalPathsFile:
		externalPathsInformation = decoder.JSONDecoder().decode(externalPathsFile.read())

		distributionReleasesRelativePath = externalPathsInformation.get("DistributionReleasesPath", None)  # type: str

		if distributionReleasesRelativePath is not None:
			DistributionReleasesPath = os.path.normpath(os.path.abspath(os.path.join(AutomationPath, distributionReleasesRelativePath)))
		
		distributionPreviewsRelativePath = externalPathsInformation.get("DistributionPreviewsPath", None)  # type: str

		if distributionPreviewsRelativePath is not None:
			DistributionPreviewsPath = os.path.normpath(os.path.abspath(os.path.join(AutomationPath, distributionPreviewsRelativePath)))

		websitesDistributionRelativePath = externalPathsInformation.get("WebsitesDistributionPath", None)  # type: str

		if websitesDistributionRelativePath is not None:
			WebsitesDistributionPath = os.path.normpath(os.path.abspath(os.path.join(AutomationPath, websitesDistributionRelativePath)))

S4UserDataPath = _GetS4UserDataPath()  # type: str
S4ModsPath = os.path.join(S4UserDataPath, "Mods")  # type: str

AutomationPath = os.path.dirname(os.path.dirname(os.path.normpath(__file__)))  # type: str
STBLCollisionsPath = os.path.join(AutomationPath, "STBL Collisions")  # type: str
SettingsPath = os.path.join(AutomationPath, "Settings")  # type: str

StrippingPath = os.path.join(AutomationPath, "Stripping")  # type: str
StrippingEnvironmentFilePath = os.path.join(StrippingPath, "Environment.json")  # type: str
StrippingModsFilePath = os.path.join(StrippingPath, "Mods.json")  # type: str
StrippingSitesFilePath = os.path.join(StrippingPath, "Sites.json")  # type: str

RootPath = os.path.dirname(AutomationPath)  # type: str

ApplicationPath = os.path.join(RootPath, "Applications")  # type: str

ModsPath = os.path.join(RootPath, "Mods")  # type: str
SitesPath = os.path.join(RootPath, "Websites")

PublishingPath = os.path.join(RootPath, "Publishing")  # type: str

DistributionReleasesPath = None  # type: typing.Optional[str]
DistributionPreviewsPath = None  # type: typing.Optional[str]
WebsitesDistributionPath = None  # type: typing.Optional[str]

_SetupExternalPaths()

