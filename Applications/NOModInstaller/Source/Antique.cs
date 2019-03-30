using System;
using System.Collections.Generic;
using System.IO;

namespace NOModInstaller {
	public static class Antique {
		private static Dictionary<string, Func<string, string>> Parsers {
			get; set;
		}

		static Antique () {
			Parsers = new Dictionary<string, Func<string, string>>() {
				{
					"PlainText",
					new Func<string, string>(ParsePlainText)
				}
			};
		}

		public static IO.PathContainer GetIdentifyingFile () {
			IO.PathContainer filePath = null;

			foreach(Mod.AntiqueVersionFile versionFile in Mod.AntiqueVersionFiles) {
				if(File.Exists(versionFile.FullPath.GetPath())) {
					if(filePath != null) {
						throw new Exception("Found multiple version files");
					}

					filePath = versionFile.FullPath;
				}
			}

			return filePath;
		}

		public static string GetVersion () {
			string version = null;

			foreach(Mod.AntiqueVersionFile versionFile in Mod.AntiqueVersionFiles) {
				if(File.Exists(versionFile.FullPath.GetPath())) {
					if(version != null) {
						throw new Exception("Found multiple version files");
					}

					version = Parsers[versionFile.Format](versionFile.FullPath.GetPath());
				}
			}

			return version;
		}

		private static string ParsePlainText (string filePath) {
			return File.ReadAllText(filePath);
		}
	}
}
