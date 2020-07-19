using System.Collections.Generic;
using System.IO;
using System.IO.Compression;
using System.Reflection;

namespace NOModInstaller {
	public static class Mod {
		public static string Name {
			get; private set;
		}

		public static UninstallerPath[] UninstallerPaths {
			get; private set;
		}

		public static AntiqueVersionFile[] AntiqueVersionFiles {
			get; private set;
		}

		public static AntiqueFileList[] AntiqueFileLists {
			get; private set;
		}

		public static string[] UniqueFileNames {
			get; private set;
		}

		static Mod () {
			Assembly executingAssembly = Assembly.GetExecutingAssembly();

			using(StreamReader nameStream = new StreamReader(executingAssembly.GetManifestResourceStream(Entry.Namespace + ".Mod.Name.txt"))) {
				Name = nameStream.ReadToEnd();
			}

			using(StreamReader uninstallerPathsStream = new StreamReader(executingAssembly.GetManifestResourceStream(Entry.Namespace + ".Mod.Uninstaller Paths.xml"))) {
				UninstallerPaths = (UninstallerPath[])XML.Read<UninstallerPath[]>(uninstallerPathsStream.ReadToEnd());
			}

			using(StreamReader antiqueVersionFilesStream = new StreamReader(executingAssembly.GetManifestResourceStream(Entry.Namespace + ".Mod.Antique Version Files.xml"))) {
				AntiqueVersionFiles = (AntiqueVersionFile[])XML.Read<AntiqueVersionFile[]>(antiqueVersionFilesStream.ReadToEnd());
			}

			using(StreamReader antiqueFileListsStream = new StreamReader(executingAssembly.GetManifestResourceStream(Entry.Namespace + ".Mod.Antique File Lists.xml"))) {
				AntiqueFileLists = (AntiqueFileList[])XML.Read<AntiqueFileList[]>(antiqueFileListsStream.ReadToEnd());
			}

			using(StreamReader uniqueFileNamesStream = new StreamReader(executingAssembly.GetManifestResourceStream(Entry.Namespace + ".Mod.Unique File Names.txt"))) {
				UniqueFileNames = Tools.NormalizeLineEndings(uniqueFileNamesStream.ReadToEnd(), "\n").Split('\n');
			}
		}

		public static IO.PathContainer[] GetValidUninstallerPaths () {
			List<IO.PathContainer> validUninstallerPaths = new List<IO.PathContainer>();

			for(int uninstallerPathIndex = 0; uninstallerPathIndex < UninstallerPaths.Length; uninstallerPathIndex++) {
				validUninstallerPaths.AddRange(UninstallerPaths[uninstallerPathIndex].FindValidPaths());
			}

			return validUninstallerPaths.ToArray();
		}

		public static IO.PathContainer[] GetValidUniqueFilePaths () {
			List<IO.PathContainer> validUniqueFilePaths = new List<IO.PathContainer>();

			for(int uniqueFileNameIndex = 0; uniqueFileNameIndex < UniqueFileNames.Length; uniqueFileNameIndex++) {
				validUniqueFilePaths.AddRange(IO.SearchForFilesNamed(Paths.ModsPath.ToString(), UniqueFileNames[uniqueFileNameIndex], 2));
			}

			return validUniqueFilePaths.ToArray();
		}

		public static ZipArchive GetFilesArchive () {
			Assembly executingAssembly = Assembly.GetExecutingAssembly();

			return new ZipArchive(executingAssembly.GetManifestResourceStream(Entry.Namespace + ".Mod.Files.zip"));
		}

		public class AntiqueVersionFile {
			public string Path {
				get; set;
			}

			public IO.PathContainer FullPath {
				get {
					return new IO.PathContainer(System.IO.Path.Combine(Paths.ModsPath.GetPath(), Path));
				}
			}

			public string Format {
				get; set;
			}
		}

		public class AntiqueFileList {
			public string Version {
				get; set;
			}

			public List<string> Files {
				get; set;
			}

			public List<IO.PathContainer> GetFilesFullPaths () {
				List<IO.PathContainer> fileList = new List<IO.PathContainer>();

				for(int fileIndex = 0; fileIndex < Files.Count; fileIndex++) {
					fileList.Add(new IO.PathContainer(Path.Combine(Paths.ModsPath.GetPath(), Files[fileIndex])));
				}

				return fileList;
			}
		}

		public enum UninstallerPathType {
			RelativeToMods = 0,
			UniqueFileName = 1
		}

		public class UninstallerPath {
			public string Path {
				get; set;
			}

			public UninstallerPathType Type {
				get; set;
			}

			public List<IO.PathContainer> FindValidPaths () {
				List<IO.PathContainer> validPaths = new List<IO.PathContainer>();

				if(Type == UninstallerPathType.RelativeToMods) {
					IO.PathContainer uninstallerPathObject = new IO.PathContainer(System.IO.Path.Combine(Paths.ModsPath.ToString(), Path));

					if(File.Exists(uninstallerPathObject.ToString())) {
						validPaths.Add(uninstallerPathObject);
					}
				} else if(Type == UninstallerPathType.UniqueFileName) {
					validPaths.AddRange(IO.SearchForFilesNamed(Paths.ModsPath.ToString(), Path, 2));
				}

				return validPaths;
			}
		}
	}
}
