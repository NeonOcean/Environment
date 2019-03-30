from Automation import Mods, Publishing

def Run () -> bool:
	namespace = "NeonOcean.Cycle"  # type: str

	Mods.BuildMod(namespace)
	Mods.BuildPublishing(namespace)
	Publishing.PublishModPreview(namespace)

	return True

if __name__ == "__main__":
	if not Run():
		exit(1)
