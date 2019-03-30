from Automation import Sites

def Run () -> bool:
	for site in Sites.GetAllSiteNames():  # type: str
		Sites.BuildSite(site)

	return True

if __name__ == "__main__":
	if not Run():
		exit(1)
