import argparse
import os
import sys
import tkinter
import typing
from tkinter import filedialog

from Decompiler import Decompile

def Run () -> bool:
	global _targetPath, _destinationPath, _silent

	argumentParser = argparse.ArgumentParser(description = "Decompile a directory for python 3.7")  # type: argparse.ArgumentParser
	argumentParser.add_argument("-t", metavar = "target", type = str, help = "The target directory path.")
	argumentParser.add_argument("-d", metavar = "destination", type = str, help = "The directory the decompiled files will be saved to.")
	argumentParser.add_argument("-s", action = "store_true", help = "Prevents gui from appearing.")
	argumentDictionary = vars(argumentParser.parse_args(sys.argv[1:]))  # type: argparse.Namespace

	if argumentDictionary["t"] is not None:
		if not os.path.exists(argumentDictionary["t"]):
			print("'" + argumentDictionary["t"] + "' is not an existent directory.")
			return False

	if argumentDictionary["d"] is not None:
		try:
			if not os.path.exists(argumentDictionary["d"]):
				os.makedirs(argumentDictionary["d"])
		except:
			print("Cannot create destination directory at '" + argumentDictionary["d"] + "'")
			return False

	_targetPath = argumentDictionary["t"]
	_destinationPath = argumentDictionary["d"]
	_silent = argumentDictionary["s"]

	tkRoot = tkinter.Tk()
	tkRoot.withdraw()

	targetDirectory = filedialog.askdirectory(initialdir = os.path.dirname(os.path.realpath(__file__)), title = "Select decompile target directory")  # type: str

	if not targetDirectory:
		return False

	targetDirectory = os.path.abspath(targetDirectory)

	destinationDirectory = filedialog.askdirectory(initialdir = targetDirectory if targetDirectory else os.path.dirname(os.path.realpath(__file__)), title = "Select destination directory")  # type: str

	if not destinationDirectory:
		return False

	destinationDirectory = os.path.abspath(destinationDirectory)

	failedFiles = list()  # type: typing.List[str]

	for directoryRoot, directoryNames, fileNames in os.walk(targetDirectory):  # type: str, list, list
		for fileName in fileNames:  # type: str
			filePath = os.path.join(directoryRoot, fileName)  # type: str
			fileExtension = os.path.splitext(fileName)[1]  # type: str
			Extension = fileExtension.casefold()

			if Extension == ".pyc":
				if not Decompile.DecompileFileToDirectory(filePath, directoryRoot.replace(targetDirectory, destinationDirectory)):
					failedFiles.append(filePath.replace(targetDirectory + os.sep, ""))

	if len(failedFiles) == 0:
		print("All files decompiled successfully.")
	else:
		failedString = "\nDecompile results: \nFailed files\n" + _FormatListToLines(failedFiles)  # type: str
		print(failedString)

	return True

def _FormatListToLines (targetList: typing.List[str]) -> str:
	text = ""  # type: str

	for target in targetList:
		if text == "":
			text += target
		else:
			text += "\n" + target

	return text

_targetPath = None  # type: str
_destinationPath = None  # type: str
_silent = False  # type: str

if __name__ == "__main__":
	if not Run():
		exit(1)
