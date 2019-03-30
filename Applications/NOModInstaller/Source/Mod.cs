using System;
using System.Collections.Generic;
using System.IO;
using System.IO.Compression;
using System.Reflection;

namespace NOModInstaller {
	public static class Mod {
		public static string Name {
			get; private set;
		}

		public static IO.PathContainer UninstallerPath {
			get; private set;
		}

		public static AntiqueVersionFile[] AntiqueVersionFiles {
			get; private set;
		}

		public static AntiqueFileList[] AntiqueFileLists {
			get; private set;
		}

		static Mod () {
			Assembly executingAssembly = Assembly.GetExecutingAssembly();

			using(StreamReader nameStream = new StreamReader(executingAssembly.GetManifestResourceStream(Entry.Namespace + ".Mod.Name.txt"))) {
				Name = nameStream.ReadToEnd();
			}

			using(StreamReader uninstallerPathStream = new StreamReader(executingAssembly.GetManifestResourceStream(Entry.Namespace + ".Mod.Uninstaller Path.txt"))) {
				UninstallerPath = new IO.PathContainer(uninstallerPathStream.ReadToEnd());
			}

			using(StreamReader antiqueVersionFilesStream = new StreamReader(executingAssembly.GetManifestResourceStream(Entry.Namespace + ".Mod.Antique Version Files.xml"))) {
				AntiqueVersionFiles = (AntiqueVersionFile[])XML.Read<AntiqueVersionFile[]>(antiqueVersionFilesStream.ReadToEnd());
			}

			using(StreamReader antiqueFileListsStream = new StreamReader(executingAssembly.GetManifestResourceStream(Entry.Namespace + ".Mod.Antique File Lists.xml"))) {
				AntiqueFileLists = (AntiqueFileList[])XML.Read<AntiqueFileList[]>(antiqueFileListsStream.ReadToEnd());
			}
		}

		public static IO.PathContainer GetUninstallerFullPath () {
			return new IO.PathContainer(Path.Combine(Paths.ModsPath.GetPath(), UninstallerPath.GetPath()));
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
	}
}
