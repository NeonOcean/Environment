import sys
import os
import typing

from Automation import Paths

_modPaths = dict()  # type: typing.Dict[str, str]
_sitePaths = dict()  # type: typing.Dict[str, str]

def GetAllModNames () -> typing.List[str]:
	modNameList = list()  # type: typing.List[str]

	for modName, modPath in _modPaths.items():  # type: str, str
		modNameList.append(modName)

	return modNameList

def GetAllModPaths () -> typing.List[str]:
	modPathList = list()  # type: typing.List[str]

	for modName, modPath in _modPaths.items():  # type: str, str
		modPathList.append(modPath)

	return modPathList

def GetModPath (namespace: str) -> str:
	namespaceLower = namespace.lower()  # type: str
	modPath = None  # type: str

	for checkingModName, checkingModPath in _modPaths.items():  # type: str, str
		if namespaceLower == checkingModName.lower():
			modPath = checkingModPath

	if modPath is None:
		raise Exception("Missing mod '" + namespaceLower + "'.")

	return modPath

def GetAllSiteNames () -> typing.List[str]:
	siteNameList = list()  # type: typing.List[str]

	for siteName, sitePath in _sitePaths.items():  # type: str, str
		siteNameList.append(siteName)

	return siteNameList

def GetAllSitePaths () -> typing.List[str]:
	sitePathList = list()  # type: typing.List[str]

	for siteName, sitePath in _sitePaths.items():  # type: str, str
		sitePathList.append(sitePath)

	return sitePathList

def GetSitePath (namespace: str) -> str:
	namespaceLower = namespace.lower()  # type: str
	sitePath = None  # type: str

	for checkingSiteName, checkingSitePath in _sitePaths.items():  # type: str, str
		if namespaceLower == checkingSiteName.lower():
			sitePath = checkingSitePath

	if sitePath is None:
		raise Exception("Missing site '" + namespaceLower + "'.")

	return sitePath

def _Setup () -> None:
	#Setup mods
	pythonPathsLower = list(sys.path)  # type: typing.List[str]

	for pythonPathsLowerIndex in range(0, len(pythonPathsLower)):
		pythonPathsLower[pythonPathsLowerIndex] = pythonPathsLower[pythonPathsLowerIndex].lower()

	for modFolderName in os.listdir(Paths.ModsPath):  # type: str
		modPath = os.path.join(Paths.ModsPath, modFolderName)  # type: str

		if os.path.isdir(modPath):
			_modPaths[modFolderName] = modPath

		if not modPath.lower() in pythonPathsLower:
			sys.path.append(os.path.join(modPath, "Automation", os.path.split(modPath)[1]))


	#Setup sites
	pythonPathsLower = list(sys.path)  # type: typing.List[str]

	for pythonPathsLowerIndex in range(0, len(pythonPathsLower)):
		pythonPathsLower[pythonPathsLowerIndex] = pythonPathsLower[pythonPathsLowerIndex].lower()

	for siteFolderName in os.listdir(Paths.SitesPath):  # type: str
		sitePath = os.path.join(Paths.SitesPath, siteFolderName)  # type: str

		if os.path.isdir(sitePath):
			_sitePaths[siteFolderName] = sitePath

		if not sitePath.lower() in pythonPathsLower:
			sys.path.append(os.path.join(sitePath, "Automation", os.path.split(sitePath)[1]))

_Setup()