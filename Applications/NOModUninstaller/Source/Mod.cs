using System.Collections.Generic;
using System.IO;
using System.Windows.Forms;

namespace NOModUninstaller {
	public static class Mod {
		public static string ModName {
			get; private set;
		}

		public static IO.PathContainer FileListPath {
			get; private set;
		}

		public static IO.PathContainer ConfigPath {
			get; private set;
		}

		public static string[] FileList {
			get; private set;
		}

		static Mod () {
			ModName = Properties.Settings.Default.ModName;
			FileListPath = new IO.PathContainer(Path.Combine(Path.GetDirectoryName(Application.ExecutablePath), "Files.txt"));
			ConfigPath = new IO.PathContainer(Path.Combine(Path.GetDirectoryName(Application.ExecutablePath), Path.GetFileName(Application.ExecutablePath) + ".config"));

			try {
				if(File.Exists(FileListPath.GetPath())) {
					FileList = File.ReadAllLines(FileListPath.GetPath());
				}
			} catch { }
		}

		public static List<IO.PathContainer> GetFileListFullPaths () {
			List<IO.PathContainer> fileList = new List<IO.PathContainer>();

			if(FileList == null) {
				return fileList;
			}

			for(int fileIndex = 0; fileIndex < FileList.Length; fileIndex++) {
				fileList.Add(new IO.PathContainer(Path.Combine(Paths.ModsPath.GetPath(), FileList[fileIndex])));
			}

			return fileList;
		}
	}
}
