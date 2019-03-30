from Automation import Sites, Publishing

def Run () -> bool:
	namespace = "NeonOcean.NOC.Main"  # type: str

	Sites.BuildSite(namespace)
	Publishing.PublishSite(namespace)

	return True

if __name__ == "__main__":
	if not Run():
		exit(1)
