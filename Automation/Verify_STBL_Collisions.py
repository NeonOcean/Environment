from Automation.Testing import STBL

def Run () -> bool:
	STBL.VerifyCollisions()

	return True

if __name__ == "__main__":
	if not Run():
		exit(1)