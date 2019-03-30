import importlib
import os
import sys
import typing

from Automation import Paths

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

def BuildMod (namespace: str) -> None:
	buildModule = importlib.import_module("Mod_" + namespace.replace(".", "_") + ".Main")
	buildModule.BuildMod("Normal")

def BuildPublishing (namespace: str) -> None:
	buildModule = importlib.import_module("Mod_" + namespace.replace(".", "_") + ".Main")
	buildModule.BuildPublishing()

def _Setup () -> None:
	pythonPathsLower = list(sys.path)  # type: typing.List[str]

	for pythonPathsLowerIndex in range(0, len(pythonPathsLower)):
		pythonPathsLower[pythonPathsLowerIndex] = pythonPathsLower[pythonPathsLowerIndex].lower()

	for modFolderName in os.listdir(Paths.ModsPath):  # type: str
		modPath = os.path.join(Paths.ModsPath, modFolderName)  # type: str

		if os.path.isdir(modPath):
			_modPaths[modFolderName] = modPath

		if not modPath.lower() in pythonPathsLower:
			sys.path.append(os.path.join(modPath, "Automation", os.path.split(modPath)[1]))

_modPaths = dict()  # type: typing.Dict[str, str]

_Setup()
