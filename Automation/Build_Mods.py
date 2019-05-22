from Automation import Mods

def Run () -> bool:
	for modNamespace in Mods.GetAllModNames():  # type: str
		Mods.BuildMod(modNamespace)

	return True

if __name__ == "__main__":
	if not Run():
		exit(1)
