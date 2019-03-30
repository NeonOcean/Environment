import datetime
import os
import re
import typing
from json import decoder

from Automation import Mods, Paths

class ModVersion:
	def __init__ (self, versionString: str, versionDirectoryPath: str, baseDirectoryPath: str, concealerFolderName: str = None):
		versionDirectoryPath = os.path.normpath(versionDirectoryPath)
		baseDirectoryPath = os.path.normpath(baseDirectoryPath)

		versionMatch = _versionParseRegex.match(versionString)

		if not versionMatch:
			raise ValueError("Invalid version number '%s'" % versionString)

		self.Version = versionString  # type: str

		self.VersionNumber = int("{}{}{}{}".format(*versionMatch.groups("0")))  # type: int

		with open(os.path.join(versionDirectoryPath, "information.json")) as informationFile:
			information = decoder.JSONDecoder().decode(informationFile.read())

			gameVersion = information["Game Version"]  # type: str

			if not _versionParseRegex.match(gameVersion):
				raise ValueError("Invalid game version number '%s'" % gameVersion)

			self.GameVersion = gameVersion  # type: str

			releaseDate = information["Release Date"]  # type: str

			datetime.date.fromisoformat(releaseDate)

			self.ReleaseDate = releaseDate  # type: str

		self.ConcealerFolderName = concealerFolderName  # type: str

		installerDirectoryPath = os.path.join(versionDirectoryPath, "installer")  # type: str

		if not os.path.exists(installerDirectoryPath):
			raise Exception("Missing installer distribution directory in '" + versionDirectoryPath + "'.")

		for installerFileName in os.listdir(installerDirectoryPath):  # type: str
			if hasattr(self, "InstallerFilePath"):
				raise Exception("Found multiple installer distribution files in '" + installerDirectoryPath + "'.")

			installerFilePath = os.path.join(installerDirectoryPath, installerFileName)  # type: str
			installerFilePath = installerFilePath[installerFilePath.lower().index(baseDirectoryPath.lower() + os.path.sep) + len(baseDirectoryPath) + 1:]
			installerFilePath = installerFilePath.replace("\\", "/")

			self.InstallerFilePath = installerFilePath

		if not hasattr(self, "InstallerFilePath"):
			raise Exception("Found no installer distribution file in '" + installerDirectoryPath + "'.")

		filesDirectoryPath = os.path.join(versionDirectoryPath, "files")  # type: str

		if not os.path.exists(filesDirectoryPath):
			raise Exception("Missing files distribution directory in '" + versionDirectoryPath + "'.")

		for filesFileName in os.listdir(filesDirectoryPath):  # type: str
			if hasattr(self, "filesFilePath"):
				raise Exception("Found multiple files distribution files in '" + filesDirectoryPath + "'.")

			filesFilePath = os.path.join(filesDirectoryPath, filesFileName)  # type: str
			filesFilePath = filesFilePath[filesFilePath.lower().index(baseDirectoryPath.lower() + os.path.sep) + len(baseDirectoryPath) + 1:]
			filesFilePath = filesFilePath.replace("\\", "/")

			self.FilesFilePath = filesFilePath

		if not hasattr(self, "FilesFilePath"):
			raise Exception("Found no files distribution file in '" + filesDirectoryPath + "'.")

		sourcesDirectoryPath = os.path.join(versionDirectoryPath, "sources")  # type: str

		if not os.path.exists(sourcesDirectoryPath):
			raise Exception("Missing sources distribution directory in '" + versionDirectoryPath + "'.")

		for sourcesFileName in os.listdir(sourcesDirectoryPath):  # type: str
			if hasattr(self, "SourcesFilePath"):
				raise Exception("Found multiple sources distribution files in '" + sourcesDirectoryPath + "'.")

			sourcesFilePath = os.path.join(sourcesDirectoryPath, sourcesFileName)  # type: str
			sourcesFilePath = sourcesFilePath[sourcesFilePath.lower().index(baseDirectoryPath.lower() + os.path.sep) + len(baseDirectoryPath) + 1:]
			sourcesFilePath = sourcesFilePath.replace("\\", "/")

			self.SourcesFilePath = sourcesFilePath

		if not hasattr(self, "SourcesFilePath"):
			raise Exception("Found no sources distribution file in '" + sourcesDirectoryPath + "'.")

def GetReleaseVersions (namespace: str) -> typing.Optional[typing.List[ModVersion]]:
	versions = _GetMod(namespace, Releases)  # type: typing.List[ModVersion]

	return versions

def GetReleaseLatest (namespace: str) -> typing.Optional[ModVersion]:
	versions = _GetMod(namespace, Releases)  # type: typing.List[ModVersion]

	if versions is None:
		return None

	latestVersion = None  # type: ModVersion
	for version in versions:  # type: ModVersion
		if latestVersion is None:
			latestVersion = version

		if latestVersion.VersionNumber < version.VersionNumber:
			latestVersion = version

	return latestVersion

def GetPreviewVersions (namespace: str) -> typing.Optional[typing.List[ModVersion]]:
	versions = _GetMod(namespace, Previews)  # type: typing.List[ModVersion]

	return versions

def GetPreviewLatest (namespace: str) -> typing.Optional[ModVersion]:
	versions = _GetMod(namespace, Previews)  # type: typing.List[ModVersion]

	if versions is None:
		return None

	latestVersion = None  # type: ModVersion
	for version in versions:  # type: ModVersion
		if latestVersion is None:
			latestVersion = version

		if latestVersion.VersionNumber < version.VersionNumber:
			latestVersion = version

	return latestVersion

def _GetMod (namespace: str, dictionary: typing.Dict[str, typing.List[ModVersion]]) -> typing.Optional[typing.List[ModVersion]]:
	namespaceLower = namespace.lower()  # type: str

	for checkingNamespace, checkingVersions in dictionary.items():  # type: str, typing.List[ModVersion]
		if checkingNamespace.lower() == namespaceLower:
			return dictionary[checkingNamespace]

	return None

def _Setup () -> None:
	validModNames = Mods.GetAllModNames()  # type: typing.List[str]
	validModNamesLower = list()  # type: typing.List[str]

	for validModNameIndex in range(len(validModNames)):
		validModNamesLower.append(validModNames[validModNameIndex].lower())

	for modName in os.listdir(Paths.DistributionReleasesPath):  # type: str
		modNameLower = modName.lower()  # type: str

		validModFolder = False  # type: bool
		for validModName in validModNames:  # type: str
			if validModName.lower() == modNameLower:
				validModFolder = True
				modName = validModName
				break

		if not validModFolder:
			continue

		modPath = os.path.join(Paths.DistributionReleasesPath, modName)  # type: str

		modVersions = list()  # type: typing.List[ModVersion]

		for modVersionName in os.listdir(modPath):  # type: str
			modVersionPath = os.path.join(modPath, modVersionName)  # type: str

			modVersions.append(ModVersion(os.path.split(modVersionPath)[1], modVersionPath, Paths.DistributionReleasesPath))

		Releases[modName] = modVersions

	for modName in os.listdir(Paths.DistributionPreviewsPath):  # type: str
		if not modName.lower() in validModNamesLower:
			continue

		modPath = os.path.join(Paths.DistributionPreviewsPath, modName)  # type: str

		modVersions = list()  # type: typing.List[ModVersion]

		for modVersionName in os.listdir(modPath):  # type: str
			modVersionPath = os.path.join(modPath, modVersionName)  # type: str

			modRandomPaths = os.listdir(modVersionPath)  # type: str

			if len(modRandomPaths) != 1:
				raise Exception("Missing random folder or too many folders for version at '" + modVersionPath + "'.")

			modRandomPath = os.path.join(modVersionPath, modRandomPaths[0])

			modVersions.append(ModVersion(os.path.split(modVersionPath)[1], modRandomPath, Paths.DistributionPreviewsPath, modRandomPaths[0]))

		Previews[modName] = modVersions

	for modNamespace, modReleaseVersions in Releases.items():  # type: str, typing.List[ModVersion]
		modPreviewVersions = _GetMod(modNamespace, Previews)  # type: typing.List[ModVersion]

		if modPreviewVersions is None:
			continue

		for modReleaseVersion in modReleaseVersions:  # type: ModVersion
			for modPreviewVersion in modPreviewVersions:  # type: ModVersion
				if modReleaseVersion.VersionNumber == modPreviewVersion.VersionNumber:
					raise Exception(modNamespace + " version exists in the release distribution and the preview distribution.\nVersion: " + str(modReleaseVersion.VersionNumber))

_versionParseRegex = re.compile(r'^(\d+) \. (\d+) (?:\. (\d+))? (?:\. (\d+))?$', re.VERBOSE | re.ASCII)

Releases = dict()  # type: typing.Dict[str, typing.List[ModVersion]]
Previews = dict()  # type: typing.Dict[str, typing.List[ModVersion]]

_Setup()
