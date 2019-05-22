import importlib
import typing
import sys

from Automation import Setup
from Automation.Tools import Exceptions

_sites = list()  # type: typing.List[Site]

class Site:
	def __init__ (self, namespace: str):
		self.Namespace = namespace  # type: str
		self.Path = GetSitePath(namespace)  # type: str

		try:
			self.Module = _GetSiteModule(namespace)  # type: typing.Optional
		except Exception as e:
			if type(e) is not ModuleNotFoundError:
				print("Failed to import site module for '" + self.Namespace + "'\n" + Exceptions.FormatException(e), file = sys.stderr)

			self.Module = None  # type: typing.Optional

		self.Data = _GetSiteData(self.Module)  # type: typing.Dict[str, typing.Any]

		try:
			self.BuildModule = _GetBuildModule(namespace) # type: typing.Optional
		except Exception as e:
			if type(e) is not ModuleNotFoundError:
				print("Failed to import site build module for '" + self.Namespace + "'\n" + Exceptions.FormatException(e), file = sys.stderr)

			self.BuildModule = None  # type: typing.Optional

		self._buildFunction = _GetBuildFunction(self.BuildModule)  # type: typing.Optional[typing.Callable[[], bool]]
		self._buildPublishingFunction = _GetBuildPublishingFunction(self.BuildModule)  # type: typing.Optional[typing.Callable[[], bool]]

		_sites.append(self)

	def Build (self) -> bool:
		if self._buildFunction is None:
			print("Tried to build the site '" + self.Namespace + "' but it is disabled as no build function is available.", file = sys.stderr)
			return False

		return self._buildFunction()

	def BuildPublishing (self) -> bool:
		if self._buildPublishingFunction is None:
			print("Tried to build publishing for the site '" + self.Namespace + "' but it is disabled as no build function is available.", file = sys.stderr)
			return False

		return self._buildPublishingFunction()

	def GetDomain (self) -> typing.Optional[str]:
		return self.Data.get("Domain")

	def GetGithubName (self) -> typing.Optional[str]:
		return self.Data.get("GithubName")

	def GetBuildPath (self) -> typing.Optional[str]:
		return self.Data.get("BuildPath")

	def GetHostingPath (self) -> typing.Optional[str]:
		return self.Data.get("HostingPath")

def GetSite (namespace: str) -> Site:
	for site in _sites:  # type: Site
		if site.Namespace == namespace:
			return site

	raise Exception("Failed to find the site '" + namespace + "' in the site list.")

def GetAllSiteNames () -> typing.List[str]:
	return Setup.GetAllSiteNames()

def GetAllSitePaths () -> typing.List[str]:
	return Setup.GetAllSitePaths()

def GetSitePath (namespace: str) -> str:
	return Setup.GetSitePath(namespace)

def BuildSite (namespace: str) -> None:
	GetSite(namespace).Build()

def BuildPublishing (namespace: str) -> None:
	GetSite(namespace).BuildPublishing()

def _GetSiteModule (namespace: str):
	return importlib.import_module("Site_" + namespace.replace(".", "_") + ".Site")

def _GetBuildModule (namespace: str):
	return importlib.import_module("Site_" + namespace.replace(".", "_") + ".Main")

def _GetSiteData (siteModule: typing.Optional) -> typing.Dict[str, typing.Any]:
	if siteModule is None:
		return dict()

	if hasattr(siteModule, "GetSiteData"):
		return siteModule.GetSiteData()

	return dict()

def _GetBuildFunction (buildModule: typing.Optional) -> typing.Optional[typing.Callable[[str], bool]]:
	if buildModule is None:
		return None

	if hasattr(buildModule, "BuildSite"):
		return buildModule.BuildSite

def _GetBuildPublishingFunction (buildModule: typing.Optional) -> typing.Optional[typing.Callable[[str], bool]]:
	if buildModule is None:
		return None

	if hasattr(buildModule, "BuildPublishing"):
		return buildModule.BuildPublishing

def _Setup () -> None:
	for siteNamespace in Setup.GetAllSiteNames():
		Site(siteNamespace)

_Setup()