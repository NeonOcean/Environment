import importlib
import os
import sys
import typing

from Automation import Mods, Paths

def VerifyCollisions () -> None:
	print("Verifying STBL collisions.")

	staticHashes = list()  # type: typing.List[int]

	for hashesFileName in os.listdir(Paths.STBLCollisionsPath):  # type: str
		hashesFilePath = os.path.join(Paths.STBLCollisionsPath, hashesFileName)  # type: str

		with open(hashesFilePath) as hashesFile:
			for staticHash in hashesFile.readlines():
				staticHashes.append(int(staticHash))

	modEntries = list()  # type: typing.List[typing.Tuple[str, int]]

	for mod in Mods.GetAllModNames():  # type: str
		try:
			stblModule = importlib.import_module("Mod_" + mod.replace(".", "_") + ".STBL")
		except:
			continue

		modEntries.extend(stblModule.GetEntries())

	for entryIdentifier, entryHash in modEntries:  # type: str, int
		if entryHash in staticHashes:
			print("Colliding STBL hash for entry '" + entryIdentifier + "'. Entry hash code: " + ConvertIntegerToHexadecimal(entryHash, minimumLength = 8), file = sys.stderr)

	for entryIndex, entry in enumerate(modEntries):  # type: int, typing.Tuple[str, int]
		for checkingEntryIndex, checkingEntry in enumerate(modEntries):  # type: int, typing.Tuple[str, int]
			if entryIndex == checkingEntryIndex:
				continue

			if entry[1] == checkingEntry[1]:
				print("Colliding STBL hash between entry '" + entry[0] + "'. and '" + checkingEntry[0] + "' Entry hash code: " + ConvertIntegerToHexadecimal(entry[1], minimumLength = 8), file = sys.stderr)

def ConvertIntegerToHexadecimal (integer: int, minimumLength: int = -1) -> str:
	hexString = hex(integer)[2:]

	if len(hexString) < minimumLength:
		hexString = "0" * (minimumLength - len(hexString)) + hexString

	hexString = hexString.upper()

	return "0x" + hexString
