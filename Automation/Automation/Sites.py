import importlib
import os
import sys
import typing

from Automation import Paths

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

def BuildSite (namespace: str) -> None:
	buildModule = importlib.import_module("Site_" + namespace.replace(".", "_") + ".Main")
	buildModule.BuildSite()

def _Setup () -> None:
	pythonPathsLower = list(sys.path)  # type: typing.List[str]

	for pythonPathsLowerIndex in range(0, len(pythonPathsLower)):
		pythonPathsLower[pythonPathsLowerIndex] = pythonPathsLower[pythonPathsLowerIndex].lower()

	for siteFolderName in os.listdir(Paths.SitesPath):  # type: str
		sitePath = os.path.join(Paths.SitesPath, siteFolderName)  # type: str

		if os.path.isdir(sitePath):
			_sitePaths[siteFolderName] = sitePath

		if not sitePath.lower() in pythonPathsLower:
			sys.path.append(os.path.join(sitePath, "Automation", os.path.split(sitePath)[1]))

_sitePaths = dict()  # type: typing.Dict[str, str]

_Setup()
