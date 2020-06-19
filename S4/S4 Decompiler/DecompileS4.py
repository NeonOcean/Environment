import argparse
import importlib
import os
import platform
import shutil
import sys
import tkinter
import typing
import uuid
import zipfile
from importlib import machinery, util
from tkinter import filedialog, messagebox

from Decompiler import Decompile
from rope.base import project
from rope.refactor import rename

def Run () -> bool:
	global _s4InstallPath, _destinationPath, _silent

	argumentParser = argparse.ArgumentParser(description = "Decompiles most Sims 4 python files automatically")  # type: argparse.ArgumentParser
	argumentParser.add_argument("-i", metavar = "install", type = str, help = "The Sims 4 install directory.")
	argumentParser.add_argument("-d", metavar = "destination", type = str, help = "The directory the decompiled files will be saved to.")
	argumentParser.add_argument("-s", action = "store_true", help = "Prevents gui from appearing.")
	argumentDictionary = vars(argumentParser.parse_args(sys.argv[1:]))  # type: typing.Dict[str, typing.Any]

	if argumentDictionary["i"] is not None:
		if not os.path.exists(argumentDictionary["i"]):
			print("'" + argumentDictionary["i"] + "' is not an existent directory.")
			return False

	if argumentDictionary["d"] is not None:
		try:
			if not os.path.exists(argumentDictionary["d"]):
				os.makedirs(argumentDictionary["d"])
		except:
			print("Cannot create destination directory at '" + argumentDictionary["d"] + "'")
			return False

	_s4InstallPath = argumentDictionary["i"]
	_destinationPath = argumentDictionary["d"]
	_silent = argumentDictionary["s"]

	if sys.version_info[0] != 3 or sys.version_info[1] != 7:
		if not _silent:
			messagebox.showerror("Wrong python version", "This decompiler must be run on python version 3.7 \nCurrently running version: '" + str(sys.version_info[0]) + "." + str(sys.version_info[1]) + "'")
		else:
			print("This decompiler must be run on python version 3.7 \nCurrently running version: '" + str(sys.version_info[0]) + "." + str(sys.version_info[1]) + "'", file = sys.stderr)

		return False

	tkRoot = tkinter.Tk()
	tkRoot.withdraw()

	if _s4InstallPath is None:
		_s4InstallPath = _GetS4InstallPath()  # type: str

	if not _s4InstallPath:
		print("Failed to find The Sims 4 install directory.", file = sys.stderr)
		return False

	if _destinationPath is None:
		if not _silent:
			_destinationPath = filedialog.askdirectory(initialdir = os.path.dirname(os.path.realpath(__file__)), title = "Select an output directory")  # type: str

	if not _destinationPath:
		print("No output destination specified.", file = sys.stderr)
		return False

	_destinationPath = os.path.normpath(_destinationPath)

	return _Main()

def _Main () -> bool:
	s4PythonPath = os.path.join(_s4InstallPath, "Data", "Simulation", "Gameplay")  # type: str
	tempPath = os.path.join(os.getenv("TEMP"), "NeonOceanS4Decompiler" + str(uuid.uuid4()))  # type: str

	baseS4Path = os.path.join(s4PythonPath, "Base.zip")  # type: str
	baseTempPath = os.path.join(tempPath, "Base")  # type: str

	if not os.path.exists(baseS4Path):
		print("Cannot find Sims 4 python archive 'base.zip'", file = sys.stderr)
		return False

	baseFailedFiles = _TransferBase(baseS4Path, baseTempPath, _destinationPath)  # type: typing.List[str]

	coreS4Path = os.path.join(s4PythonPath, "Core.zip")  # type: str
	coreTempPath = os.path.join(tempPath, "Core")  # type: str

	if not os.path.exists(coreS4Path):
		print("Cannot find Sims 4 python archive 'core.zip'", file = sys.stderr)
		return False

	coreFailedFiles = _DecompileCore(coreS4Path, coreTempPath, _destinationPath)  # type: typing.List[str]

	generatedS4Path = os.path.join(_s4InstallPath, "Game", "Bin", "Python", "Generated.zip")
	generatedTempPath = os.path.join(tempPath, "Generated")  # type: str

	if not os.path.exists(generatedS4Path):
		print("Cannot find Sims 4 python archive 'generated.zip'", file = sys.stderr)
		return False

	generatedFailedFiles = _DecompileGenerated(generatedS4Path, generatedTempPath, _destinationPath)  # type: typing.List[str]

	simulationS4Path = os.path.join(s4PythonPath, "Simulation.zip")  # type: str
	simulationTempPath = os.path.join(tempPath, "Simulation")  # type: str

	if not os.path.exists(coreS4Path):
		print("Cannot find Sims 4 python archive 'simulation.zip'", file = sys.stderr)
		return False

	simulationFailedFiles = _DecompileSimulation(simulationS4Path, simulationTempPath, _destinationPath)  # type: typing.List[str]

	if len(baseFailedFiles) == 0 and len(coreFailedFiles) == 0 and len(simulationFailedFiles) == 0:
		print("All files decompiled successfully.")
	else:
		baseFailedString = "Failed files in 'base.zip'\n" + _FormatListToLines(baseFailedFiles)  # type: str
		coreFailedString = "Failed files in 'core.zip'\n" + _FormatListToLines(coreFailedFiles)  # type: str
		generatedFailedString = "Failed files in 'generated.zip'\n" + _FormatListToLines(generatedFailedFiles)  # type: str
		simulationFailedString = "Failed files in 'simulation.zip'\n" + _FormatListToLines(simulationFailedFiles)  # type: str

		print("\nDecompile results:" + "\n" + \
			  baseFailedString + "\n\n" + \
			  coreFailedString + "\n\n" + \
			  generatedFailedString + "\n\n" + \
			  simulationFailedString + \
			  "\n", file = sys.stderr)

	shutil.rmtree(tempPath)

	return True

def _TransferBase (baseS4Path: str, baseTempPath: str, destinationDirectoryPath: str) -> typing.List[str]:
	# noinspection SpellCheckingInspection
	ignoredModules = [
		"__phello__.foo"
	]

	specialCases = {
		"enum_lib": _TransferBaseEnum,
		"statistics_lib": _TransferBaseStatistics
	}  # type: typing.Dict[str, typing.Callable]

	postSpecialCases = {
		"enum_lib": _PostTransferBaseEnum,
		"statistics_lib": _PostTransferBaseStatistics
	}

	requiredSpecialCases = []  # type: typing.List[typing.Callable]

	failedFiles = list()  # type: typing.List[str]

	print("Extracting python archive 'base.zip'.")

	with zipfile.ZipFile(baseS4Path) as s4PythonBaseFile:
		s4PythonBaseFile.extractall(baseTempPath)

	tempBaseLibPath = os.path.join(baseTempPath, "Lib")  # type: str
	destinationBaseLibPath = os.path.join(destinationDirectoryPath, "base", "lib")  # type: str

	print("Transferring base python files using archive 'base.zip' as a template.")

	for directoryRoot, directoryNames, fileNames in os.walk(os.path.join(tempBaseLibPath)):  # type: str, typing.List[str], typing.List[str]
		for fileName in fileNames:  # type: str
			if os.path.splitext(fileName)[1].casefold() == ".pyc":
				filePath = os.path.join(directoryRoot, fileName)  # type: str
				relativeFilePath = filePath.replace(tempBaseLibPath + os.sep, "")  # type: str

				moduleName = os.path.splitext(relativeFilePath)[0].replace(os.sep, ".")  # type: str

				if moduleName in ignoredModules:
					continue

				moduleSpecialCase = specialCases.get(moduleName)  # type: typing.Optional[typing.Callable]
				modulePostSpecialCase = postSpecialCases.get(moduleName)  # type: typing.Optional[typing.Callable]

				if moduleSpecialCase is not None:
					if not moduleSpecialCase(destinationBaseLibPath):
						failedFiles.append(relativeFilePath)
						continue

					if modulePostSpecialCase is not None:
						requiredSpecialCases.append(postSpecialCases[moduleName])

					continue

				if modulePostSpecialCase is not None:
					requiredSpecialCases.append(postSpecialCases[moduleName])

				moduleSpecification = None  # type: typing.Optional[machinery.ModuleSpec]

				try:
					moduleSpecification = util.find_spec(moduleName)
				except:
					pass

				if moduleSpecification is None:
					print("No module named '" + moduleName + "' could be found.", file = sys.stderr)
					failedFiles.append(relativeFilePath)
					continue

				outputFilePath = os.path.join(destinationBaseLibPath, os.path.splitext(relativeFilePath)[0] + ".py")  # type: str
				outputDirectoryPath = os.path.dirname(outputFilePath)  # type: str

				if moduleSpecification.has_location:
					if not os.path.exists(outputDirectoryPath):
						os.makedirs(outputDirectoryPath)

					shutil.copy(moduleSpecification.origin, outputFilePath)
				else:
					module = importlib.import_module(moduleName)  # type: any

					if not hasattr(module, "__file__"):
						print("Module '" + moduleName + "' has no listed file location.", file = sys.stderr)
						failedFiles.append(relativeFilePath)
						continue

					if not os.path.exists(outputDirectoryPath):
						os.makedirs(outputDirectoryPath)

					shutil.copy(importlib.import_module(moduleName).__file__, outputFilePath)

	for requiredSpecialCase in requiredSpecialCases:  # type: typing.Callable
		requiredSpecialCase(destinationBaseLibPath)

	return failedFiles

def _TransferBaseEnum (destinationBaseLibPath: str) -> bool:
	moduleName = "enum"  # type: str

	moduleSpecification = None  # type: typing.Optional[machinery.ModuleSpec]

	try:
		moduleSpecification = util.find_spec(moduleName)
	except:
		pass

	if moduleSpecification is None:
		print("No module named '" + moduleName + "' could be found.", file = sys.stderr)
		return False

	outputFilePath = os.path.join(destinationBaseLibPath, moduleName.replace(".", os.path.sep) + ".py")  # type: str
	outputDirectoryPath = os.path.dirname(outputFilePath)  # type: str

	if moduleSpecification.has_location:
		if not os.path.exists(outputDirectoryPath):
			os.makedirs(outputDirectoryPath)

		shutil.copy(moduleSpecification.origin, outputFilePath)
	else:
		module = importlib.import_module(moduleName)  # type: any

		if not hasattr(module, "__file__"):
			print("Module '" + moduleName + "' has no listed file location.", file = sys.stderr)
			return False

		if not os.path.exists(outputDirectoryPath):
			os.makedirs(outputDirectoryPath)

		shutil.copy(importlib.import_module(moduleName).__file__, outputFilePath)

	return True

def _PostTransferBaseEnum (destinationBaseLibPath: str) -> None:
	moduleName = "enum"  # type: str
	moduleNewName = "enum_lib"  # type: str

	baseProject = project.Project(destinationBaseLibPath)  # type: project.Project
	baseChanges = rename.Rename(baseProject, baseProject.find_module(moduleName)).get_changes(moduleNewName, docs = True)
	baseProject.do(baseChanges)
	baseProject.close()

	# noinspection SpellCheckingInspection
	ropeProjectPath = destinationBaseLibPath + os.path.sep + ".ropeproject"  # type: str

	try:
		if os.path.exists(ropeProjectPath):
			shutil.rmtree(ropeProjectPath)
	except Exception as e:
		print("Failed to remove the rope project directory at '" + ropeProjectPath + "'.\n" + str(e))

def _TransferBaseStatistics (destinationBaseLibPath: str) -> bool:
	moduleName = "statistics"  # type: str

	moduleSpecification = None  # type: typing.Optional[machinery.ModuleSpec]

	try:
		moduleSpecification = util.find_spec(moduleName)
	except:
		pass

	if moduleSpecification is None:
		print("No module named '" + moduleName + "' could be found.", file = sys.stderr)
		return False

	outputFilePath = os.path.join(destinationBaseLibPath, moduleName.replace(".", os.path.sep) + ".py")  # type: str
	outputDirectoryPath = os.path.dirname(outputFilePath)  # type: str

	if moduleSpecification.has_location:
		if not os.path.exists(outputDirectoryPath):
			os.makedirs(outputDirectoryPath)

		shutil.copy(moduleSpecification.origin, outputFilePath)
	else:
		module = importlib.import_module(moduleName)  # type: any

		if not hasattr(module, "__file__"):
			print("Module '" + moduleName + "' has no listed file location.", file = sys.stderr)
			return False

		if not os.path.exists(outputDirectoryPath):
			os.makedirs(outputDirectoryPath)

		shutil.copy(importlib.import_module(moduleName).__file__, outputFilePath)

	return True

def _PostTransferBaseStatistics (destinationBaseLibPath: str) -> None:
	moduleName = "statistics"  # type: str
	moduleNewName = "statistics_lib"  # type: str

	baseProject = project.Project(destinationBaseLibPath)  # type: project.Project
	baseChanges = rename.Rename(baseProject, baseProject.find_module(moduleName)).get_changes(moduleNewName, docs = True)
	baseProject.do(baseChanges)
	baseProject.close()

	# noinspection SpellCheckingInspection
	ropeProjectPath = destinationBaseLibPath + os.path.sep + ".ropeproject"  # type: str

	try:
		if os.path.exists(ropeProjectPath):
			shutil.rmtree(ropeProjectPath)
	except Exception as e:
		print("Failed to remove the rope project directory at '" + ropeProjectPath + "'.\n" + str(e))

def _DecompileCore (coreS4Path: str, coreTempPath: str, destinationDirectoryPath: str) -> typing.List[str]:
	failedFiles = list()  # type: typing.List[str]

	print("Extracting python archive 'core.zip'.")

	with zipfile.ZipFile(coreS4Path) as s4PythonCoreFile:
		s4PythonCoreFile.extractall(coreTempPath)

	print("Decompiling python archive 'core.zip'.")

	destinationCorePath = os.path.join(destinationDirectoryPath, "core")  # type: str

	for directoryRoot, directoryNames, fileNames in os.walk(os.path.join(coreTempPath)):  # type: str, typing.List[str], typing.List[str]
		for fileName in fileNames:  # type: str
			if os.path.splitext(fileName)[1].casefold() == ".pyc":
				filePath = os.path.join(directoryRoot, fileName)  # type: str
				relativeFilePath = filePath.replace(coreTempPath + os.sep, "")  # type: str

				outputDirectoryPath = os.path.join(destinationCorePath, os.path.dirname(relativeFilePath))  # type: str
				outputDirectoryPath = os.path.normpath(outputDirectoryPath)  # type: str

				if not Decompile.DecompileFileToDirectory(filePath, outputDirectoryPath, printFileName = os.path.join("core.zip", relativeFilePath)):
					failedFiles.append(relativeFilePath)

	return failedFiles

def _DecompileGenerated (generatedS4Path, generatedTempPath, destinationDirectoryPath) -> typing.List[str]:
	failedFiles = list()  # type: typing.List[str]

	print("Extracting python archive 'generated.zip'.")

	with zipfile.ZipFile(generatedS4Path) as s4PythonGeneratedFile:
		s4PythonGeneratedFile.extractall(generatedTempPath)

	print("Decompiling python archive 'generated.zip'.")

	destinationGeneratedPath = os.path.join(destinationDirectoryPath, "generated")  # type: str

	for directoryRoot, directoryNames, fileNames in os.walk(os.path.join(generatedTempPath)):  # type: str, typing.List[str], typing.List[str]
		for fileName in fileNames:  # type: str
			if os.path.splitext(fileName)[1].casefold() == ".pyc":
				filePath = os.path.join(directoryRoot, fileName)  # type: str
				relativeFilePath = filePath.replace(generatedTempPath + os.sep, "")  # type: str

				outputDirectoryPath = os.path.join(destinationGeneratedPath, os.path.dirname(relativeFilePath))  # type: str
				outputDirectoryPath = os.path.normpath(outputDirectoryPath)  # type: str

				if not Decompile.DecompileFileToDirectory(filePath, outputDirectoryPath, printFileName = os.path.join("generated.zip", relativeFilePath)):
					failedFiles.append(relativeFilePath)

	return failedFiles

def _DecompileSimulation (simulationS4Path: str, simulationTempPath: str, destinationDirectoryPath: str) -> typing.List[str]:
	failedFiles = list()  # type: typing.List[str]

	print("Extracting python archive 'simulation.zip'.")

	with zipfile.ZipFile(simulationS4Path) as s4PythonSimulationFile:
		s4PythonSimulationFile.extractall(simulationTempPath)

	print("Decompiling python archive 'simulation.zip'.")

	destinationSimulationPath = os.path.join(destinationDirectoryPath, "simulation")  # type: str

	for directoryRoot, directoryNames, fileNames in os.walk(os.path.join(simulationTempPath)):  # type: str, typing.List[str], typing.List[str]
		for fileName in fileNames:  # type: str
			if os.path.splitext(fileName)[1].casefold() == ".pyc":
				filePath = os.path.join(directoryRoot, fileName)  # type: str
				relativeFilePath = filePath.replace(simulationTempPath + os.sep, "")  # type: str

				outputDirectoryPath = os.path.join(destinationSimulationPath, os.path.dirname(relativeFilePath))  # type: str
				outputDirectoryPath = os.path.normpath(outputDirectoryPath)  # type: str

				if not Decompile.DecompileFileToDirectory(filePath, outputDirectoryPath, printFileName = os.path.join("simulation.zip", relativeFilePath)):
					failedFiles.append(relativeFilePath)

	return failedFiles

def _GetS4InstallPath () -> typing.Optional[str]:
	if platform.system() == "Windows":
		import winreg

		entryDirectory = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, "Software\\Maxis\\The Sims 4")  # type: winreg.HKEYType
		installDirectoryPath = winreg.QueryValueEx(entryDirectory, "Install Dir")[0]  # type: str
		entryDirectory.Close()
	else:
		tkRoot = tkinter.Tk()
		tkRoot.withdraw()

		installDirectoryPath = None  # type: typing.Optional[str]

		if not _silent:
			installDirectoryPath = filedialog.askdirectory(initialdir = os.path.dirname(os.path.realpath(__file__)), title = "Select The Sims 4 install directory")

		if installDirectoryPath is None:
			return None

		installDirectoryPath = os.path.normpath(installDirectoryPath)

	return os.path.normpath(installDirectoryPath)

def _FormatListToLines (targetList: typing.List[str]) -> str:
	text = ""  # type: str

	for target in targetList:
		if text == "":
			text += target
		else:
			text += "\n" + target

	return text

_s4InstallPath = None  # type: typing.Optional[str]
_destinationPath = None  # type: typing.Optional[str]
_silent = False  # type: bool

if __name__ == "__main__":
	if not Run():
		exit(1)
