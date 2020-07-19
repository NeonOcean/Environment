using System;
using System.Collections.Generic;
using System.IO;
using System.Text.RegularExpressions;

namespace NOModInstaller {
	public static class IO {
		public static string NormalizePath (string path) {
			string pathNormalized = path.Replace(Path.AltDirectorySeparatorChar, Path.DirectorySeparatorChar);
			pathNormalized = pathNormalized.Trim(Path.DirectorySeparatorChar);
			pathNormalized = Regex.Replace(pathNormalized, @"\" + Path.DirectorySeparatorChar + "{1,}", Path.DirectorySeparatorChar.ToString());

			return pathNormalized;
		}

		public static bool CloseDirectory (string directoryPath) {
			if(!Directory.Exists(directoryPath)) {
				return true;
			}

			return CloseDirectoryInternal(directoryPath);
		}

		private static bool CloseDirectoryInternal (string directoryPath) {
			string[] files = Directory.GetFiles(directoryPath);
			string[] subDirectories = Directory.GetDirectories(directoryPath);

			bool closedAllSubDirectories = true;

			for(int subDirectoryIndex = 0; subDirectoryIndex < subDirectories.Length; subDirectoryIndex++) {
				if(!CloseDirectoryInternal(subDirectories[subDirectoryIndex])) {
					closedAllSubDirectories = false;
				}
			}

			if(!closedAllSubDirectories) {
				return false;
			}

			if(files.Length == 0) {
				Directory.Delete(directoryPath, true);
			} else {
				return false;
			}

			return true;
		}

		public static void DeleteFiles (IEnumerable<string> filePaths) {
			foreach(string filePath in filePaths) {
				if(File.Exists(filePath)) {
					File.Delete(filePath);
				}
			}
		}

		public static void DeleteFiles (IEnumerable<PathContainer> filePaths) {
			foreach(PathContainer filePath in filePaths) {
				if(File.Exists(filePath.GetPath())) {
					File.Delete(filePath.GetPath());
				}
			}
		}

		public static void MoveDirectory (string sourcePath, string targetPath) {
			if(!Directory.Exists(sourcePath)) {
				return;
			}

			Directory.CreateDirectory(targetPath);

			foreach(string sourceFile in Directory.GetFiles(sourcePath)) {
				string sourceFileTarget = Path.Combine(targetPath, Path.GetFileName(sourceFile));

				if(File.Exists(sourceFileTarget)) {
					File.Delete(sourceFileTarget);
				}

				File.Move(sourceFile, sourceFileTarget);
			}

			foreach(string subDirectory in Directory.GetDirectories(sourcePath)) {
				MoveDirectory(subDirectory, Path.Combine(targetPath, Path.GetFileName(subDirectory)));
			}
		}

		public static List<PathContainer> SearchForFilesNamed (string searchingDirectoryPath, string fileName, int maximumRecursion) {
			List<PathContainer> matchingFilePaths = new List<PathContainer>();

			string matchingFilePath = Path.Combine(searchingDirectoryPath, fileName);
			if(File.Exists(matchingFilePath)) {
				matchingFilePaths.Add(new PathContainer(matchingFilePath));
			}

			if(maximumRecursion > 0) {
				foreach(string searchingSubDirectoryName in Directory.GetDirectories(searchingDirectoryPath)) {
					string searchingSubDirectoryPath = Path.Combine(searchingDirectoryPath, searchingSubDirectoryName);

					matchingFilePaths.AddRange(SearchForFilesNamed(searchingSubDirectoryPath, fileName, maximumRecursion - 1));
				}
			}

			return matchingFilePaths;
		}

		public class PathContainer {
			public int Length {
				get {
					return Segments.Length;
				}
			}

			private string[] Segments {
				get; set;
			} = new string[0];

			private string FullPath {
				get; set;
			} = "";

			private PathContainer (string[] segments) {
				Segments = segments;
				FullPath = Combine(Segments);
			}

			public PathContainer (string path) {
				Segments = NormalizePath(path).Split(Path.DirectorySeparatorChar);
				FullPath = Combine(Segments);
			}

			public string[] GetSegments () {
				string[] segmentsCopy = new string[Segments.Length];
				Segments.CopyTo(segmentsCopy, 0);
				return segmentsCopy;
			}

			public bool IsChildOf (string path) {
				return IsChildOf(new PathContainer(path));
			}

			public bool IsChildOf (PathContainer path) {
				if(path.Segments.Length >= Segments.Length) {
					return false;
				}

				for(int segmentIndex = 0; segmentIndex < path.Segments.Length; segmentIndex++) {
					if(!path.Segments[segmentIndex].Equals(Segments[segmentIndex], StringComparison.OrdinalIgnoreCase)) {
						return false;
					}
				}

				return true;
			}

			public PathContainer GetRelativePathTo (string path) {
				return GetRelativePathTo(new PathContainer(path));
			}

			public PathContainer GetRelativePathTo (PathContainer path) {
				if(!IsChildOf(path)) {
					throw new NotChildException();
				}

				string[] segmentsCopy = new string[Segments.Length - path.Segments.Length];
				Array.Copy(Segments, path.Segments.Length, segmentsCopy, 0, Segments.Length - path.Segments.Length);
				PathContainer relativePath = new PathContainer(segmentsCopy);
				return relativePath;
			}

			public string GetPath () {
				return FullPath;
			}

			public string GetPath (int length) {
				if(length == 0) {
					return "";
				}

				if(length < 0 || length >= Segments.Length) {
					return GetPath();
				}

				string path = "";

				for(int segmentIndex = 0; segmentIndex < length; segmentIndex++) {
					if(segmentIndex == 0) {
						path = Segments[segmentIndex];
					} else {
						path = Combine(path, Segments[segmentIndex]);
					}
				}

				return path;
			}

			public override bool Equals (object obj) {
				if(obj.GetType() != typeof(PathContainer)) {
					return false;
				}

				return Equals((PathContainer)obj);
			}

			public bool Equals (string path) {
				if(path == null) {
					return false;
				}

				return Equals(new PathContainer(path));
			}

			public bool Equals (PathContainer path) {
				if(path == null) {
					return false;
				}

				if(path.Segments.Length != Segments.Length) {
					return false;
				}

				for(int segmentIndex = 0; segmentIndex < path.Segments.Length; segmentIndex++) {
					if(!path.Segments[segmentIndex].Equals(Segments[segmentIndex], StringComparison.OrdinalIgnoreCase)) {
						return false;
					}
				}

				return true;
			}

			public override int GetHashCode () {
				string segmentsCombined = "";

				for(int segmentIndex = 0; segmentIndex < Segments.Length; segmentIndex++) {
					segmentsCombined += Segments[segmentIndex];
				}

				return segmentsCombined.ToLower().GetHashCode();
			}

			public override string ToString () {
				return GetPath();
			}

			private static string Combine (params string[] segments) {
				string path = "";

				for(int segmentIndex = 0; segmentIndex < segments.Length; segmentIndex++) {
					if(segmentIndex == 0) {
						path = segments[segmentIndex];
					} else {
						path = path + Path.DirectorySeparatorChar + segments[segmentIndex];
					}
				}

				return path;
			}

			private static string Combine (string segment1, string segment2) {
				return segment1 + Path.DirectorySeparatorChar + segment2;
			}

			[Serializable]
			public class NotChildException : Exception {
				public NotChildException () {
				}

				public NotChildException (string message) : base(message) { }

				public NotChildException (string message, Exception inner) : base(message, inner) { }

				protected NotChildException (
				  System.Runtime.Serialization.SerializationInfo info,
				  System.Runtime.Serialization.StreamingContext context) : base(info, context) { }
			}
		}
	}
}
