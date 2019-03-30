from Automation import Publishing

def Run () -> bool:
	Publishing.VerifyStripping()

	return True

if __name__ == "__main__":
	if not Run():
		exit(1)