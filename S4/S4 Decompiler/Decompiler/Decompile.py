import multiprocessing
import os
import sys
import threading
import typing
from multiprocessing import connection

from uncompyle6 import main
from unpyc37 import unpyc3

_decompileProcess = None  # type: typing.Optional[multiprocessing.Process]
_decompileProcessInputPipe = None  # type: typing.Optional[connection.Connection]
_decompileProcessOutputPipe = None  # type: typing.Optional[connection.Connection]

def DecompileFileToDirectory (targetFilePath: str, destinationDirectoryPath: str, printFileName: str = None) -> bool:
	if threading.current_thread() != threading.main_thread():
		raise Exception("This function is not thread safe.")

	if not os.path.exists(destinationDirectoryPath):
		os.makedirs(destinationDirectoryPath)

	targetFileName = os.path.split(targetFilePath)[1]  # type: str
	destinationFilePath = os.path.join(destinationDirectoryPath, os.path.splitext(targetFileName)[0] + ".py")  # type: str

	try:
		completed = _DecompileFileInternal(targetFilePath, destinationFilePath, printFileName = printFileName)  # type: bool

		if not completed:
			if printFileName is None:
				printFileName = targetFilePath

			print("Failed to decompile '" + printFileName + "'.", file = sys.stderr)

		return completed
	except Exception as e:
		if printFileName is None:
			printFileName = targetFilePath

		print("Failed to decompile '" + printFileName + "'. " + str(e), file = sys.stderr)

		global _decompileProcess, _decompileProcessInputPipe, _decompileProcessOutputPipe

		if _decompileProcess is not None:
			_decompileProcess = None

		if _decompileProcessInputPipe is not None:
			_decompileProcessInputPipe = None

		if _decompileProcessOutputPipe is not None:
			_decompileProcessOutputPipe = None

		return False

def DecompileFile (targetFilePath: str, destinationFilePath: str, printFileName: str = None) -> bool:
	if threading.current_thread() != threading.main_thread():
		raise Exception("This function is not thread safe.")

	try:
		completed = _DecompileFileInternal(targetFilePath, destinationFilePath, printFileName = printFileName)  # type: bool

		if not completed:
			if printFileName is None:
				printFileName = targetFilePath

			print("Failed to decompile '" + printFileName + "'.", file = sys.stderr)
		return completed
	except Exception as e:
		if printFileName is None:
			printFileName = targetFilePath

		print("Failed to decompile '" + printFileName + "'. " + str(e), file = sys.stderr)

		global _decompileProcess, _decompileProcessInputPipe, _decompileProcessOutputPipe

		if _decompileProcess is not None:
			_decompileProcess = None

		if _decompileProcessInputPipe is not None:
			_decompileProcessInputPipe = None

		if _decompileProcessOutputPipe is not None:
			_decompileProcessOutputPipe = None

		return False

def _DecompileFileInternal (targetFilePath: str, destinationFilePath: str, printFileName: str = None) -> bool:
	global _decompileProcess, _decompileProcessInputPipe, _decompileProcessOutputPipe

	if threading.current_thread() != threading.main_thread():
		raise Exception("This function is not thread safe.")

	timeoutTime = 30  # type: int

	resetProcess = False  # type: bool
	if _decompileProcess is None or not _decompileProcess.is_alive() or \
			_decompileProcessInputPipe is None or \
			_decompileProcessOutputPipe is None:
		resetProcess = True

	if resetProcess:
		if _decompileProcess is not None:
			_decompileProcess.terminate()
			_decompileProcess = None

		if _decompileProcessInputPipe is not None:
			_decompileProcessInputPipe.close()
			_decompileProcessInputPipe = None

		if _decompileProcessOutputPipe is not None:
			_decompileProcessOutputPipe.close()
			_decompileProcessOutputPipe = None

		processInputConnectionOut, processInputConnectionIn = multiprocessing.Pipe(False)
		processOutputConnectionOut, processOutputConnectionIn = multiprocessing.Pipe(False)
		process = multiprocessing.Process(target = _DecompileFileProcess, args = (processInputConnectionOut, processOutputConnectionIn,))
		process.daemon = True

		_decompileProcess = process
		_decompileProcessInputPipe = processInputConnectionIn
		_decompileProcessOutputPipe = processOutputConnectionOut

		process.start()

	_decompileProcessInputPipe.send({
		"targetFilePath": targetFilePath,
		"destinationFilePath": destinationFilePath,
		"printFileName": printFileName
	})

	if _decompileProcessOutputPipe.poll(timeoutTime):
		report = _decompileProcessOutputPipe.recv()  # type: bool
		return report
	else:
		_decompileProcessInputPipe.close()
		_decompileProcessInputPipe = None
		_decompileProcessOutputPipe.close()
		_decompileProcessOutputPipe = None
		_decompileProcess.terminate()
		_decompileProcess = None

		raise Exception("Decompiler was still active after specified timeout of " + str(timeoutTime) + " seconds we have to terminate it.")

def _DecompileFileProcess (inputPipe: connection.Connection, outputPipe: connection.Connection) -> None:
	"""
	Intended to run in a separate process don't call this directly.
	"""

	while True:
		inputPipe.poll(None)

		request = inputPipe.recv()  # type: dict

		targetFilePath = request["targetFilePath"]  # type: str
		destinationFilePath = request["destinationFilePath"]  # type: str
		printFileName = request["printFileName"]  # type: str

		if printFileName is None:
			printFileName = targetFilePath

		try:
			with open(destinationFilePath, "w+", encoding = "utf-8") as destinationFile:
				destinationFile.write(str(unpyc3.decompile(targetFilePath)))
		except Exception as e:
			print("Failed to decompile '", printFileName + "' with 'unpyc3' trying alternative 'uncompyle6'. \n" + str(e), file = sys.stderr)

			try:
				with open(destinationFilePath, "w+", encoding = "utf-8") as destinationFile:
					main.decompile_file(targetFilePath, outstream = destinationFile)
			except Exception as e:
				print("uncompyle6 failed to decompile '", printFileName + "'. \n" + str(e), file = sys.stderr)

				outputPipe.send(False)
				continue

		outputPipe.send(True)
		continue
