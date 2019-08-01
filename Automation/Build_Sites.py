from Automation import Sites
import datetime

def Run () -> bool:
	for siteNamespace in Sites.GetAllSiteNames():  # type: str
		Sites.BuildSite(siteNamespace)

	print("All sites built. " + datetime.datetime.now().strftime("%I:%M %p"))

	return True

if __name__ == "__main__":
	if not Run():
		exit(1)
