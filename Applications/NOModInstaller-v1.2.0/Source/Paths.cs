using System;
using System.IO;

namespace NOModInstaller {
	public static class Paths {
		public static IO.PathContainer Sims4Path {
			get {
				return sims4Path;
			}

			set {
				sims4Path = value;

				if(value == null) {
					Sims4OptionsPath = null;
					ModsPath = null;
				} else {
					Sims4OptionsPath = new IO.PathContainer(Path.Combine(sims4Path.GetPath(), "Options.ini"));
					ModsPath = new IO.PathContainer(Path.Combine(sims4Path.GetPath(), "Mods"));
				}
			}
		}

		public static IO.PathContainer Sims4OptionsPath {
			get; private set;
		} = null;

		public static IO.PathContainer ModsPath {
			get; private set;
		} = null;

		public static IO.PathContainer TemporaryPath {
			get; private set;
		}

		private static IO.PathContainer sims4Path = null;

		private static string[] possibleSims4DirectoryNames = new string[] {
			"The Sims 4",
			"Los Sims 4",
			"Des Sims 4",
			"Die Sims 4",
			"Les Sims 4",
			"De Sims 4"
		};

		static Paths () {
			string appropriateSims4Path = FindAppropriateSims4Path();

			if(appropriateSims4Path != null) {
				Sims4Path = new IO.PathContainer(appropriateSims4Path);
			}

			TemporaryPath = new IO.PathContainer(Path.Combine(Path.GetTempPath(), Entry.Namespace + Guid.NewGuid().ToString()));
		}


		public static string FindAppropriateSims4Path () {
			if(Entry.Target != null) {
				return Entry.Target;
			}

			string electronicArtsPath = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.MyDocuments), "Electronic Arts");

			string existingSims4Path = null;

			foreach(string possibleSims4DirectoryName in possibleSims4DirectoryNames) {
				string possibleSims4Path = Path.Combine(electronicArtsPath, possibleSims4DirectoryName );

				if(Directory.Exists(possibleSims4Path)) {
					if(existingSims4Path != null) {
						return null; // Two valid sims 4 directories exist, we should let the user decide which one to use.
					}

					existingSims4Path = possibleSims4Path;



				}
			}

			return existingSims4Path;
		}
	}
}
