from Automation import Mods
import datetime

def Run () -> bool:
	for modNamespace in Mods.GetAllModNames():  # type: str
		Mods.BuildModRebuild(modNamespace)

	print("All mods built. " + datetime.datetime.now().strftime("%I:%M %p"))

	return True

if __name__ == "__main__":
	if not Run():
		exit(1)

