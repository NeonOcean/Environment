import os
import platform
import sys
import typing
from json import decoder

from Automation import Paths
from Automation.Tools import Registry

class Application:
	def __init__ (self, applicationPath: str):
		self.Name = os.path.split(applicationPath)[1]  # type: str
		self.PointerDirectoryPath = applicationPath  # type: str

		self.Special = ""  # type: str

		with open(os.path.join(self.PointerDirectoryPath, "Application.json")) as applicationPointerFile:
			applicationPointerDictionary = decoder.JSONDecoder().decode(applicationPointerFile.read())  # type: typing.Dict[str, typing.Any]

		special = applicationPointerDictionary.get("Special")  # type: str
		if isinstance(special, str):
			self.Special = special

		self.ExecutablePath = None  # type: typing.Union[str, None]
		self.ExecutableSpecial = None  # type: typing.Union[str, None]

		for pathDictionary in applicationPointerDictionary["Paths"]:  # type: typing.Dict[str, str]
			executableFullFilePath = None  # type: str

			executableRegistryKey = pathDictionary.get("Registry Key")  # type: str
			executableFilePath = pathDictionary.get("File Path")  # type: str
			executableSpecial = pathDictionary.get("Special")  # type: str

			registryKeyPath = None  # type: str

			if isinstance(executableRegistryKey, str):
				executableRegistryKey = executableRegistryKey.replace("/", "\\")

				if executableRegistryKey.count("") < 1:
					continue

				if platform.system() == "Windows":
					try:
						registryKeyPath = Registry.ReadRegistryFullKey(executableRegistryKey)
					except:
						pass

					if not isinstance(registryKeyPath, str) and registryKeyPath is not None:
						raise Exception("Application registry key value is not a string")

			if registryKeyPath is not None:
				if isinstance(executableFilePath, str):
					executableFullFilePath = os.path.normpath(os.path.join(registryKeyPath, executableFilePath))
				else:
					executableFullFilePath = os.path.normpath(registryKeyPath)
					pass
			else:
				if isinstance(executableFilePath, str):
					executableFullFilePath = os.path.normpath(os.path.join(self.PointerDirectoryPath, os.path.normpath(executableFilePath)))

			if executableFullFilePath is not None:
				if os.path.exists(executableFullFilePath):
					self.ExecutablePath = executableFullFilePath
					self.ExecutableSpecial = executableSpecial

		if self.ExecutablePath is None:
			print("Cannot find valid path to application '" + self.Name + "'.", file = sys.stderr)

def GetApplication (applicationName: str) -> Application:
	applicationNameLower = applicationName.lower()  # type: str

	for application in _applications:  # type: Application
		if applicationNameLower == application.Name.lower():
			return application

	raise Exception("No pointer to an application named '" + applicationName + "' exists.")

def _Setup ():
	for applicationFolderName in os.listdir(Paths.ApplicationPath):  # type: str
		applicationPath = os.path.join(Paths.ApplicationPath, applicationFolderName)

		if os.path.isdir(applicationPath):
			try:
				_applications.append(Application(applicationPath))
			except Exception as e:
				raise Exception("Failed to read application information in '" + applicationPath + "'.") from e

_applications = list()  # type: typing.List[Application]

_Setup()
