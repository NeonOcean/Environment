using System;
using System.Collections.Generic;
using System.IO;
using System.Diagnostics;
using System.Runtime.InteropServices;
using System.Windows.Forms;

namespace NOModUninstaller {
	public static class Entry {
		public static string Namespace {
			get; private set;
		}

		public static bool Completed {
			get; set;
		}

		public static IO.PathContainer ApplicationPath {
			get; private set;
		}

		public static bool Quick {
			get; private set;
		}

		public static bool Silent {
			get; private set;
		}

		public static bool Preserve {
			get; private set;
		}

		public static string Target {
			get; private set;
		}

		[STAThread]
		static void Main () {
			AppDomain.CurrentDomain.ProcessExit += OnExit;

			Namespace = "NOModUninstaller";
			ApplicationPath = new IO.PathContainer(Application.ExecutablePath);

			if(!ReadArguments()) {
				return;
			}

			if(!Silent) {
				Application.EnableVisualStyles();
				Application.SetCompatibleTextRenderingDefault(false);

				if(!Quick) {
					Application.Run(new Setup());
					return;
				}
			}

			NOModUninstaller.Main.Run();
		}

		private static void OnExit (object sender, EventArgs e) {
			if(!Completed) {
				if(Environment.ExitCode == 0) {
					Environment.ExitCode = 1;
				}
			} else {
				Environment.ExitCode = 0;
			}
		}

		public static bool SelfDestruct () {
			if(Preserve) {
				return true;
			}

			try {
				IO.PathContainer applicationDirectory = new IO.PathContainer(Path.GetDirectoryName(ApplicationPath.GetPath()));

				if(!ApplicationPath.IsChildOf(Paths.ModsPath)) {
					return true;
				}

				if(applicationDirectory.Equals(Paths.ModsPath)) {
					SelfDestructApplication();
					return true;
				}

				IO.PathContainer applicationRelativeDirectory = applicationDirectory.GetRelativePathTo(Paths.ModsPath);
				IO.CloseDirectory(Path.Combine(Paths.ModsPath.GetPath(), applicationRelativeDirectory.GetPath(1)));

				List<string> deletingDirectories = new List<string>();
				IO.PathContainer previousDirectory = null;

				for(int applicationRelativeDirectoryIndex = applicationRelativeDirectory.Length - 1; applicationRelativeDirectoryIndex >= 0; applicationRelativeDirectoryIndex--) {
					string directoryFullPath = Path.Combine(Paths.ModsPath.GetPath(), applicationRelativeDirectory.GetPath(applicationRelativeDirectoryIndex + 1));

					if(applicationRelativeDirectoryIndex == applicationRelativeDirectory.Length - 1) {
						List<string> directoryFiles = new List<string>(Directory.GetFiles(directoryFullPath));

						for(int directoryFileIndex = 0; directoryFileIndex < directoryFiles.Count; directoryFileIndex++) {
							if(ApplicationPath.Equals(directoryFiles[directoryFileIndex])) {
								directoryFiles.RemoveAt(directoryFileIndex);
								directoryFileIndex--;
								break;
							}
						}

						if(directoryFiles.Count != 0 || Directory.GetDirectories(directoryFullPath).Length != 0) {
							break;
						}
					} else {
						List<string> directorySubdirectories = new List<string>(Directory.GetDirectories(directoryFullPath));

						for(int directorySubdirectoryIndex = 0; directorySubdirectoryIndex < directorySubdirectories.Count; directorySubdirectoryIndex++) {
							if(previousDirectory.Equals(directorySubdirectories[directorySubdirectoryIndex])) {
								directorySubdirectories.RemoveAt(directorySubdirectoryIndex);
								directorySubdirectoryIndex--;
								break;
							}
						}

						if(Directory.GetFiles(directoryFullPath).Length != 0 || directorySubdirectories.Count != 0) {
							break;
						}
					}

					previousDirectory = new IO.PathContainer(directoryFullPath);
					deletingDirectories.Add(directoryFullPath);
				}

				if(previousDirectory == null) {
					SelfDestructApplication();
				} else {
					SelfDestructDirectory(deletingDirectories);
				}
			} catch(Exception e) {
				if(!Silent) {
					Error errorDialog = new Error(Localization.GetString("SelfDestructFailure"), e.ToString());
					errorDialog.ShowDialog();
				}

				return false;
			}

			return true;
		}

		private static void SelfDestructApplication () {
			Process.Start(new ProcessStartInfo() {
				FileName = "cmd.exe",
				WorkingDirectory = Paths.ModsPath.GetPath(),
				Arguments = "/C ping 127.0.0.1 -n 3 & del /q \"" + Application.ExecutablePath + "\"",
				WindowStyle = ProcessWindowStyle.Hidden,
			});
		}

		private static void SelfDestructDirectory (List<string> directories) {
			string Arguments = "/C ping 127.0.0.1 -n 3";

			for(int directoryIndex = 0; directoryIndex < directories.Count; directoryIndex++) {
				Arguments = Arguments + " & rmdir /s /q \"" + directories[directoryIndex] + "\"";
			}

			Process.Start(new ProcessStartInfo() {
				FileName = "cmd.exe",
				WorkingDirectory = Paths.ModsPath.GetPath(),
				Arguments = Arguments,
				WindowStyle = ProcessWindowStyle.Hidden,
			});
		}

		private static bool ReadArguments () {
			string[] arguments = Environment.GetCommandLineArgs();

			if(arguments.Length <= 1) {
				return true;
			}

			for(int argumentIndex = 1; argumentIndex < arguments.Length; argumentIndex++) {
				if(arguments[argumentIndex].Equals("-q", StringComparison.OrdinalIgnoreCase) ||
					arguments[argumentIndex].Equals("/q", StringComparison.OrdinalIgnoreCase)) {
					Quick = true;
					continue;
				}

				if(arguments[argumentIndex].Equals("-s", StringComparison.OrdinalIgnoreCase) ||
					arguments[argumentIndex].Equals("/s", StringComparison.OrdinalIgnoreCase)) {
					Quick = true;
					Silent = true;
					continue;
				}

				if(arguments[argumentIndex].Equals("-p", StringComparison.OrdinalIgnoreCase) ||
					arguments[argumentIndex].Equals("/p", StringComparison.OrdinalIgnoreCase)) {
					Preserve = true;
					continue;
				}

				if(arguments[argumentIndex].Equals("-t", StringComparison.OrdinalIgnoreCase) ||
					arguments[argumentIndex].Equals("/t", StringComparison.OrdinalIgnoreCase)) {
					if(argumentIndex != arguments.Length - 1) {
						Target = arguments[argumentIndex + 1];
						argumentIndex++;
						continue;
					}
				}
			}

			try {
				if (Target != null) {
					try {
						Target = Path.GetFullPath(Target);
						new DirectoryInfo(Target);
					} catch {
						if (!Silent) {
							MessageBox.Show(string.Format(Localization.GetString("InvalidDirectory"), Target));
						}

						return false;
					}
				}
			} catch (Exception e) {
				throw new Exception("Failed to parse argument '-t'", e);
			}

			return true;
		}
	}
}
