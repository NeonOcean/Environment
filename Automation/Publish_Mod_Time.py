from Automation import Mods, Publishing

def Run () -> bool:
	namespace = "NeonOcean.S4.Time"  # type: str

	Mods.BuildMod(namespace)
	Mods.BuildPublishing(namespace)
	Publishing.PublishModRelease(namespace)

	return True

if __name__ == "__main__":
	if not Run():
		exit(1)
