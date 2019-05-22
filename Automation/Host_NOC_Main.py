import subprocess
import sys
import typing

from Automation import Sites

def Run () -> bool:
	namespace = "NeonOcean.NOC.Main"  # type: str

	siteHostingPath = Sites.GetSite(namespace).GetHostingPath()  # type: typing.Optional[str]

	if siteHostingPath is not None:
		subprocess.call([sys.executable, "-m" "http.server"], cwd = siteHostingPath)
	else:
		print("Cannot host the website at '" + namespace + "' as no hosting directory has been specified.", file = sys.stderr)

	return True

if __name__ == "__main__":
	if not Run():
		exit(1)
