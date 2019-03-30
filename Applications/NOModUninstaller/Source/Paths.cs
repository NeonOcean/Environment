using System;
using System.IO;

namespace NOModUninstaller {
	public static class Paths {
		public static IO.PathContainer Sims4Path {
			get {
				return sims4Path;
			}

			set {
				sims4Path = value;
				sims4OptionsPath = new IO.PathContainer(Path.Combine(sims4Path.GetPath(), "Options.ini"));
				modsPath = new IO.PathContainer(Path.Combine(sims4Path.GetPath(), "Mods"));
			}
		}

		public static IO.PathContainer Sims4OptionsPath {
			get {
				return sims4OptionsPath;
			}
		}

		public static IO.PathContainer ModsPath {
			get {
				return modsPath;
			}
		}

		private static IO.PathContainer sims4Path = null;
		private static IO.PathContainer sims4OptionsPath = null;
		private static IO.PathContainer modsPath = null;

		static Paths () {
			Sims4Path = new IO.PathContainer(Entry.Target ?? Path.Combine(new string[] { Environment.GetFolderPath(Environment.SpecialFolder.MyDocuments), "Electronic Arts", "The Sims 4" }));
		}
	}
}
