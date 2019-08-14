import importlib
import os
import sys
import typing

from Automation import Mods, Paths

def VerifyCollisions () -> None:
	print("Verifying STBL collisions.")

	staticKeys = list()  # type: typing.List[int]

	for keysFileName in os.listdir(Paths.STBLCollisionsPath):  # type: str
		keysFilePath = os.path.join(Paths.STBLCollisionsPath, keysFileName)  # type: str

		with open(keysFilePath) as keysFile:
			for staticKey in keysFile.readlines():
				staticKeys.append(int(staticKey))

	modEntries = list()  # type: typing.List[typing.Tuple[str, int]]

	for modNamespace in Mods.GetAllModNames():  # type: str
		try:
			stblModule = importlib.import_module("Mod_" + modNamespace.replace(".", "_") + ".STBL")
		except:
			continue

		modEntries.extend(stblModule.GetEntries())

	for entryIdentifier, entryKey in modEntries:  # type: str, int
		if entryKey in staticKeys:
			print("Colliding STBL key for entry '" + entryIdentifier + "'. Entry key: " + str(entryKey) + " (" + ConvertIntegerToHexadecimal(entryKey, minimumLength = 8) + ")", file = sys.stderr)

	for entryIndex, entry in enumerate(modEntries):  # type: int, typing.Tuple[str, int]
		for checkingEntryIndex, checkingEntry in enumerate(modEntries):  # type: int, typing.Tuple[str, int]
			if entryIndex == checkingEntryIndex:
				continue

			if entry[1] == checkingEntry[1]:
				print("Colliding STBL key between entry '" + entry[0] + "'. and '" + checkingEntry[0] + "' Entry key: " + str(entry[1]) + " (" + ConvertIntegerToHexadecimal(entry[1], minimumLength = 8) + ")", file = sys.stderr)

def ConvertIntegerToHexadecimal (integer: int, minimumLength: int = -1) -> str:
	hexString = hex(integer)[2:]

	if len(hexString) < minimumLength:
		hexString = "0" * (minimumLength - len(hexString)) + hexString

	hexString = hexString.upper()

	return "0x" + hexString
