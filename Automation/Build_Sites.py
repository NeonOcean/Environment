from Automation import Sites

def Run () -> bool:
	for siteNamespace in Sites.GetAllSiteNames():  # type: str
		Sites.BuildSite(siteNamespace)

	return True

if __name__ == "__main__":
	if not Run():
		exit(1)
