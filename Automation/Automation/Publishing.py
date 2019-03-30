import datetime
import getpass
import importlib
import os
import re
import sys
import typing
import uuid
import zipfile
from distutils import dir_util, file_util
from json import decoder, encoder

from Automation import Mods, Paths, S4

def VerifyStripping () -> None:
	print("Verifying stripping.")

	with open(os.path.join(Paths.AutomationPath, "Stripping.json")) as strippingFile:
		strippingInformation = decoder.JSONDecoder().decode(strippingFile.read())

	if not strippingInformation["Exclude Account Name"]:
		print("There is nothing to verify the removal of.")

	environmentIncludedPaths = GetIncludedPaths(Paths.RootPath)  # type: typing.List[str]

	_VerifyStripped(Paths.RootPath, environmentIncludedPaths)

def PublishModRelease (modNamespace: str) -> None:
	print("Publishing mod '" + modNamespace + "' as a release.")

	modModule = importlib.import_module("Mod_" + modNamespace.replace(".", "_") + ".Mod")

	modDirectoryPath = Mods.GetModPath(modNamespace)  # type: str

	version = modModule.GetVersion()  # type: str

	installerFilePath = modModule.GetInstallerFilePath()  # type: str
	filesFilePath = modModule.GetFilesFilePath()  # type: str
	sourcesFileName = modModule.GetSourcesFileName()  # type: str

	distributionVersionDirectoryPath = os.path.join(Paths.DistributionReleasesPath, modNamespace.lower(), version)  # type: str
	distributionInstallerDirectoryPath = os.path.join(distributionVersionDirectoryPath, "installer")  # type: str
	distributionFilesDirectoryPath = os.path.join(distributionVersionDirectoryPath, "files")  # type: str
	distributionSourcesDirectoryPath = os.path.join(distributionVersionDirectoryPath, "sources")  # type: str

	if os.path.exists(distributionVersionDirectoryPath):
		dir_util.remove_tree(distributionVersionDirectoryPath, verbose = 1)

	os.makedirs(distributionInstallerDirectoryPath)
	os.makedirs(distributionFilesDirectoryPath)
	os.makedirs(distributionSourcesDirectoryPath)

	file_util.copy_file(installerFilePath, distributionInstallerDirectoryPath, preserve_times = 0)
	file_util.copy_file(filesFilePath, distributionFilesDirectoryPath, preserve_times = 0)

	sourcesIncludedPaths = GetIncludedPaths(Mods.GetModPath(modNamespace))  # type: typing.List[str]

	archiveFile = zipfile.ZipFile(os.path.join(distributionSourcesDirectoryPath, sourcesFileName), mode = "w", compression = zipfile.ZIP_DEFLATED)  # type: zipfile.ZipFile

	for sourcesIncludedPath in sourcesIncludedPaths:  # type: str
		archiveFile.write(os.path.join(modDirectoryPath, sourcesIncludedPath), arcname = sourcesIncludedPath)

	archiveFile.close()

	with open(os.path.join(distributionVersionDirectoryPath, "information.json"), "w+") as versionInformationFile:
		versionInformationFile.write(encoder.JSONEncoder(indent = "\t").encode({
			"Game Version": S4.Version,
			"Release Date": datetime.datetime.now().date().isoformat()
		}))

def PublishModPreview (modNamespace: str) -> None:
	print("Publishing mod '" + modNamespace + "' as a preview.")

	modModule = importlib.import_module("Mod_" + modNamespace.replace(".", "_") + ".Mod")

	modDirectoryPath = Mods.GetModPath(modNamespace)  # type: str

	version = modModule.GetVersion()  # type: str

	installerFilePath = modModule.GetInstallerFilePath()  # type: str
	filesFilePath = modModule.GetFilesFilePath()  # type: str
	sourcesFileName = modModule.GetSourcesFileName()  # type: str

	distributionVersionDirectoryPath = os.path.join(Paths.DistributionPreviewsPath, modNamespace.lower(), version)  # type: str
	distributionConcealerDirectoryPath = os.path.join(distributionVersionDirectoryPath, str(uuid.uuid4()))  # type: str
	distributionInstallerDirectoryPath = os.path.join(distributionConcealerDirectoryPath, "installer")  # type: str
	distributionFilesDirectoryPath = os.path.join(distributionConcealerDirectoryPath, "files")  # type: str
	distributionSourcesDirectoryPath = os.path.join(distributionConcealerDirectoryPath, "sources")  # type: str

	if os.path.exists(distributionVersionDirectoryPath):
		dir_util.remove_tree(distributionVersionDirectoryPath, verbose = 1)

	os.makedirs(distributionInstallerDirectoryPath)
	os.makedirs(distributionFilesDirectoryPath)
	os.makedirs(distributionSourcesDirectoryPath)

	file_util.copy_file(installerFilePath, distributionInstallerDirectoryPath, preserve_times = 0)
	file_util.copy_file(filesFilePath, distributionFilesDirectoryPath, preserve_times = 0)

	sourcesIncludedPaths = GetIncludedPaths(Mods.GetModPath(modNamespace))  # type: typing.List[str]

	archiveFile = zipfile.ZipFile(os.path.join(distributionSourcesDirectoryPath, sourcesFileName), mode = "w", compression = zipfile.ZIP_DEFLATED)  # type: zipfile.ZipFile

	for sourcesIncludedPath in sourcesIncludedPaths:  # type: str
		archiveFile.write(os.path.join(modDirectoryPath, sourcesIncludedPath), arcname = sourcesIncludedPath)

	archiveFile.close()

	with open(os.path.join(distributionConcealerDirectoryPath, "information.json"), "w+") as versionInformationFile:
		versionInformationFile.write(encoder.JSONEncoder(indent = "\t").encode({
			"Game Version": S4.Version,
			"Release Date": datetime.datetime.now().date().isoformat()
		}))

def PublishSite (siteNamespace: str) -> None:
	print("Publishing site '" + siteNamespace + "'.")

	siteModule = importlib.import_module("Site_" + siteNamespace.replace(".", "_") + ".Site")

	buildDirectoryPath = siteModule.GetBuildPath()  # type: str
	hostingPath = os.path.join(Paths.WebsitesHostingPath, siteModule.GetGithubName() + "_Hosting")  # type: str

	if not os.path.exists(hostingPath):
		os.makedirs(hostingPath)

	if os.path.exists(hostingPath):
		for githubFileName in os.listdir(hostingPath):
			if githubFileName.startswith("."):
				continue

			hostingFilePath = os.path.join(hostingPath, githubFileName)  # type: str

			if os.path.isdir(hostingFilePath):
				dir_util.remove_tree(hostingFilePath)
			else:
				os.remove(hostingFilePath)

	for buildFileName in os.listdir(buildDirectoryPath):  # type: str
		buildFilePath = os.path.join(buildDirectoryPath, buildFileName)  # type: str
		buildFileHostingPath = os.path.join(hostingPath, buildFileName)  # type: str

		if os.path.isdir(buildFilePath):
			dir_util.copy_tree(buildFilePath, buildFileHostingPath)
		else:
			file_util.copy_file(buildFilePath, buildFileHostingPath)

def GetIncludedPaths (targetDirectoryPath: str) -> typing.List[str]:
	includedPaths = list()  # type: typing.List[str]

	with open(os.path.join(Paths.AutomationPath, "Stripping.json")) as strippingFile:
		strippingInformation = decoder.JSONDecoder().decode(strippingFile.read())

	strippingPatterns = strippingInformation["Patterns"]  # type: list

	if strippingInformation["Exclude Account Name"]:
		strippingPatterns.append(".*/" + getpass.getuser())

	for strippingPatternIndex in range(0, len(strippingPatterns)):  # type: int
		strippingPatterns[strippingPatternIndex] = re.compile(strippingPatterns[strippingPatternIndex])

	for directoryRoot, directoryNames, fileNames in os.walk(targetDirectoryPath):  # type: str, typing.List[str], typing.List[str]
		for directoryName in directoryNames:
			if directoryName.startswith("."):
				continue

			if directoryRoot != targetDirectoryPath:
				directoryPath = os.path.join(directoryRoot.replace(targetDirectoryPath + os.path.sep, ""), directoryName).replace("\\", "/")  # type: str
			else:
				directoryPath = directoryName  # type: str

			pathExcluded = False  # type: bool

			for strippingPattern in strippingPatterns:
				match = re.match(strippingPattern, directoryPath)

				if match is not None:
					pathExcluded = True
					break

			if not pathExcluded:
				includedPaths.append(directoryPath)

		for fileName in fileNames:
			if fileName.startswith("."):
				continue

			if directoryRoot != targetDirectoryPath:
				filePath = os.path.join(directoryRoot.replace(targetDirectoryPath + os.path.sep, ""), fileName).replace("\\", "/")  # type: str
			else:
				filePath = fileName  # type: str

			pathExcluded = False  # type: bool

			for strippingPattern in strippingPatterns:
				match = re.match(strippingPattern, filePath)

				if match is not None:
					pathExcluded = True
					break

			if not pathExcluded:
				includedPaths.append(filePath)

	return includedPaths

def _VerifyStripped (rootDirectoryPath: str, includedPaths: typing.List[str]) -> None:
	leakingFiles = list()  # type: typing.List[str]

	accountName = getpass.getuser()  # type: str
	accountNameLowerBytes = bytearray(accountName.lower(), "utf-8")  # type: bytearray
	accountNameUpperBytes = bytearray(accountName.upper(), "utf-8")  # type: bytearray
	accountNameBytesLength = len(accountNameLowerBytes)  # type: int

	for includedPath in includedPaths:  # type: str
		includedFullPath = os.path.join(rootDirectoryPath, includedPath)  # type: str

		if accountName.lower() in includedPath.lower():
			leakingFiles.append(includedFullPath)
			continue

		if os.path.isdir(includedFullPath):
			continue

		with open(includedFullPath, "rb") as includedFile:
			accountNamePosition = 0  # type: int

			for byte in includedFile.read():
				if byte == accountNameLowerBytes[accountNamePosition] or byte == accountNameUpperBytes[accountNamePosition]:
					if accountNamePosition >= accountNameBytesLength - 1:
						leakingFiles.append(includedFullPath)
						break
					else:
						accountNamePosition += 1
				else:
					accountNamePosition = 0

	if len(leakingFiles) != 0:
		leakingText = "Found at least " + str(len(leakingFiles)) + " potentially leaking files:"

		for leakingFile in leakingFiles:
			leakingText += "\n" + leakingFile

		print(leakingText, file = sys.stderr)
