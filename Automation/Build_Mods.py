from Automation import Mods

def Run () -> bool:
	for mod in Mods.GetAllModNames():  # type: str
		Mods.BuildMod(mod)

	return True

if __name__ == "__main__":
	if not Run():
		exit(1)
