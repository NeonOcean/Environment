import importlib
import sys
import typing

from Automation import Setup, Distribution
from Automation.Tools import Exceptions

_mods = list()  # type: typing.List[Mod]

class Mod:
	def __init__(self, namespace: str):
		self.Namespace = namespace  # type: str
		self.Path = GetModPath(namespace)  # type: str

		self.ReleaseLatest = Distribution.GetReleaseLatest(namespace)  # type: typing.Optional[Distribution.ModVersion]
		self.ReleaseVersions = Distribution.GetReleaseVersions(namespace)  # type: typing.Optional[typing.List[Distribution.ModVersion]]

		self.PreviewLatest = Distribution.GetPreviewLatest(namespace)  # type: typing.Optional[Distribution.ModVersion]
		self.PreviewVersions = Distribution.GetPreviewVersions(namespace)  # type: typing.Optional[typing.List[Distribution.ModVersion]]

		self.Game = "The Sims 4"  # type: str #TODO actually get the game for each mod.
		self.GameShortened = "S4"  # type: str # Used in website page paths

		try:
			self.Module = _GetModModule(namespace)  # type: typing.Optional
		except Exception as e:
			if type(e) is not ModuleNotFoundError:
				print("Failed to import mod module for '" + self.Namespace + "'\n" + Exceptions.FormatException(e), file = sys.stderr)

			self.Module = None  # type: typing.Optional

		self.Data = _GetModData(self.Module)  # type: typing.Dict[str, typing.Any]

		try:
			self.BuildModule = _GetBuildModule(namespace) # type: typing.Optional
		except Exception as e:
			if type(e) is not ModuleNotFoundError:
				print("Failed to import mod build module for '" + self.Namespace + "'\n" + Exceptions.FormatException(e), file = sys.stderr)

			self.BuildModule = None  # type: typing.Optional

		self._buildFunction = _GetBuildFunction(self.BuildModule)  # type: typing.Optional[typing.Callable[[str], bool]]
		self._buildPublishingFunction = _GetBuildPublishingFunction(self.BuildModule)  # type: typing.Optional[typing.Callable[[], bool]]

		_mods.append(self)

	def Build (self, modeName: str) -> bool:
		if self._buildFunction is None:
			print("Tried to build the mod '" + self.Namespace + "' but it is disabled as no build function is available.", file = sys.stderr)
			return False

		return self._buildFunction(modeName)

	def BuildPublishing (self) -> bool:
		if self._buildPublishingFunction is None:
			print("Tried to build publishing for the mod '" + self.Namespace + "' but it is disabled as no build function is available.", file = sys.stderr)
			return False

		return self._buildPublishingFunction()

	def GetVersion (self) -> typing.Optional[str]:
		return self.Data.get("Version")

	def GetName (self) -> typing.Optional[str]:
		return self.Data.get("Name")

	def GetGithubName (self) -> typing.Optional[str]:
		return self.Data.get("GithubName")

	def GetInstallerFilePath (self) -> typing.Optional[str]:
		return self.Data.get("InstallerFilePath")

	def GetFilesFilePath (self) -> typing.Optional[str]:
		return self.Data.get("FilesFilePath")

	def GetSourcesFileName (self) -> typing.Optional[str]:
		return self.Data.get("SourcesFileName")

	def GetChangesFilePath (self) -> typing.Optional[str]:
		return self.Data.get("ChangesFilePath")

	def GetPlansFilePath (self) -> typing.Optional[str]:
		return self.Data.get("PlansFilePath")

def GetMod (namespace: str) -> Mod:
	for mod in _mods:  # type: Mod
		if mod.Namespace == namespace:
			return mod

	raise Exception("Failed to find the mod '" + namespace + "' in the mod list.")

def GetAllModNames () -> typing.List[str]:
	return Setup.GetAllModNames()

def GetAllModPaths () -> typing.List[str]:
	return Setup.GetAllModPaths()

def GetModPath (namespace: str) -> str:
	return Setup.GetModPath(namespace)

def BuildMod (namespace: str) -> None:
	GetMod(namespace).Build("Normal")

def BuildModRebuild (namespace: str) -> None:
	GetMod(namespace).Build("Rebuild")

def BuildPublishing (namespace: str) -> None:
	GetMod(namespace).BuildPublishing()

def _GetModModule (namespace: str):
	return importlib.import_module("Mod_" + namespace.replace(".", "_") + ".Mod")

def _GetBuildModule (namespace: str):
	return importlib.import_module("Mod_" + namespace.replace(".", "_") + ".Main")

def _GetModData (modModule: typing.Optional) -> typing.Dict[str, typing.Any]:
	if modModule is None:
		return dict()

	if hasattr(modModule, "GetModData"):
		return modModule.GetModData()

	return dict()

def _GetBuildFunction (buildModule: typing.Optional) -> typing.Optional[typing.Callable[[str], bool]]:
	if buildModule is None:
		return None

	if hasattr(buildModule, "BuildMod"):
		return buildModule.BuildMod

def _GetBuildPublishingFunction (buildModule: typing.Optional) -> typing.Optional[typing.Callable[[str], bool]]:
	if buildModule is None:
		return None

	if hasattr(buildModule, "BuildPublishing"):
		return buildModule.BuildPublishing

def _Setup () -> None:
	for modNamespace in Setup.GetAllModNames():
		Mod(modNamespace)

_Setup()