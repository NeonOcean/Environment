import os
import sys
import argparse
import tkinter
from tkinter import filedialog, messagebox

from Decompiler import Decompile

def Run () -> bool:
	global _targetPath, _destinationPath, _silent

	argumentParser = argparse.ArgumentParser(description = "Decompile specific file for python 3.7")  # type: argparse.ArgumentParser
	argumentParser.add_argument("-t", metavar = "target", type = str, help = "The target file's path.")
	argumentParser.add_argument("-d", metavar = "destination", type = str, help = "The directory the decompiled files will be saved to.")
	argumentParser.add_argument("-s", action = "store_true", help = "Prevents gui from appearing.")
	argumentDictionary = vars(argumentParser.parse_args(sys.argv[1:]))  # type: argparse.Namespace

	if argumentDictionary["t"] is not None:
		if not os.path.exists(argumentDictionary["t"]):
			print("'" + argumentDictionary["t"] + "' is not an existent file.")
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

	if sys.version_info[0] != 3 or sys.version_info[1] != 7:
		if not _silent:
			messagebox.showerror("Wrong python version", "This decompiler must be run on python version 3.7 \nCurrently running version: '" + str(sys.version_info[0]) + "." + str(sys.version_info[1]) + "'")
		else:
			print("This decompiler must be run on python version 3.7 \nCurrently running version: '" + str(sys.version_info[0]) + "." + str(sys.version_info[1]) + "'", file = sys.stderr)

		return False

	tkRoot = tkinter.Tk()
	tkRoot.withdraw()

	if _targetPath is None:
		if not _silent:
			_targetPath = filedialog.askopenfilename(initialdir = os.path.dirname(os.path.realpath(__file__)), title = "Select the target file")  # type: str

	if not _targetPath:
		print("No target file specified.", file = sys.stderr)
		return False

	_targetPath = os.path.normpath(_targetPath)

	if _destinationPath is None:
		if not _silent:
			_destinationPath = filedialog.askdirectory(initialdir = os.path.dirname(os.path.realpath(__file__)), title = "Select an output directory")  # type: str

	if not _destinationPath:
		print("No output destination specified.", file = sys.stderr)
		return False

	_destinationPath = os.path.normpath(_destinationPath)

	return Decompile.DecompileFileToDirectory(_targetPath, _destinationPath, os.path.split(_targetPath)[1])

_targetPath = None  # type: str
_destinationPath = None  # type: str
_silent = False  # type: str

if __name__ == "__main__":
	if not Run():
		exit(1)