using Microsoft.Win32;
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Diagnostics;
using System.IO;
using System.Windows.Forms;

namespace NOModUninstaller {
	public static class Main {
		private static Func<bool>[] phases = new Func<bool>[] {
			CheckGame, DeleteFiles,
		};

		public static bool Run () {
			if(!Entry.Silent) {
				ProgressBar progressBarMenu = new ProgressBar();
				progressBarMenu.StartBackgroundWorker(Uninstall);
				progressBarMenu.ShowDialog();

				if(!progressBarMenu.Completed) {
					Abort abortMenu = new Abort();
					abortMenu.ShowDialog();

					return false;
				}
			} else {
				if(!Uninstall(null)) {
					return false;
				}
			}

			if(!Entry.Quick && !Entry.Silent) {
				Completion completionMenu = new Completion();
				completionMenu.ShowDialog();

				if(!Entry.SelfDestruct()) {
					return false;
				}
			} else {
				if(!Entry.SelfDestruct()) {
					return false;
				}
			}

			Entry.Completed = true;
			return true;
		}

		private static bool Uninstall (Action<int, string> phaseCallback) {
			for(int phaseIndex = 0; phaseIndex < phases.Length; phaseIndex++) {
				if(phaseCallback != null) {
					phaseCallback.Invoke(100 / phases.Length * (phaseIndex), "Phase" + phases[phaseIndex].Method.Name + "Text");
				}

				if(!phases[phaseIndex].Invoke()) {
					return false;
				}
			}

			if(phaseCallback != null) {
				phaseCallback.Invoke(100, "DeinstallationCompletePhaseText");
			}

			return true;
		}

		private static bool Uninstall (BackgroundWorker backgroundWorker, DoWorkEventArgs eventArgs) {
			for(int phaseIndex = 0; phaseIndex < phases.Length; phaseIndex++) {
				backgroundWorker.ReportProgress(100 / phases.Length * (phaseIndex), "Phase" + phases[phaseIndex].Method.Name + "Text");

				if(!phases[phaseIndex].Invoke()) {
					return false;
				}
			}

			backgroundWorker.ReportProgress(100, "DeinstallationCompletePhaseText");

			return true;
		}

		private static bool CheckGame () {
			try {
				string sims4InstallPath = (string)Registry.GetValue(Registry.LocalMachine + @"\SOFTWARE\Wow6432Node\Maxis\The Sims 4", "Install Dir", null);

				if(sims4InstallPath == null) {
					return true;
				}

				IO.PathContainer sims4ApplicationPath = new IO.PathContainer(Path.Combine(sims4InstallPath, "Game", "Bin", "TS4.exe"));
				IO.PathContainer sims464ApplicationPath = new IO.PathContainer(Path.Combine(sims4InstallPath, "Game", "Bin", "TS4_x64.exe"));

				Process[] processes = Process.GetProcesses();

				bool running = false;

				for(int processIndex = 0; processIndex < processes.Length; processIndex++) {
					try {
						IO.PathContainer processPath = new IO.PathContainer(Processes.GetPath(processes[processIndex]));

						if(!string.IsNullOrWhiteSpace(processPath.GetPath())) {
							if(processPath.Equals(sims4ApplicationPath) || processPath.Equals(sims464ApplicationPath)) {
								running = true;
								break;
							}
						}
					} catch { }
				}

				if(running) {
					if(!Entry.Silent) {
						MessageBox.Show(Localization.GetString("Sims4RunningText"));
					}

					return false;
				}
			} catch(Exception e) {
				if(!Entry.Silent) {
					Error errorDialog = new Error(Localization.GetString("CheckGameFailure"), e.ToString());
					errorDialog.ShowDialog();
				}

				return false;
			}

			return true;
		}

		private static bool DeleteFiles () {
			try {
				if(Mod.FileList != null) {
					List<IO.PathContainer> files = Mod.GetFileListFullPaths();
					List<IO.PathContainer> fileRoots = new List<IO.PathContainer>();

					bool removedFileListPath = false;
					bool removedConfigPath = false;

					for(int fileIndex = 0; fileIndex < files.Count; fileIndex++) {
						if(files[fileIndex].Equals(Mod.FileListPath)) {
							files.RemoveAt(fileIndex);
							fileIndex--;
							removedFileListPath = true;
							continue;
						}

						if(files[fileIndex].Equals(Mod.ConfigPath)) {
							files.RemoveAt(fileIndex);
							fileIndex--;
							removedConfigPath = true;
							continue;
						}

						if(files[fileIndex].Equals(Entry.ApplicationPath)) {
							files.RemoveAt(fileIndex);
							fileIndex--;
							continue;
						}

						IO.PathContainer fileRoot = new IO.PathContainer(Path.Combine(Paths.ModsPath.GetPath(), files[fileIndex].GetRelativePathTo(Paths.ModsPath).GetPath(1)));

						if(!fileRoots.Contains(fileRoot)) {
							fileRoots.Add(fileRoot);
						}
					}

					IO.DeleteFiles(files);

					for(int fileRootIndex = 0; fileRootIndex < fileRoots.Count; fileRootIndex++) {
						IO.CloseDirectory(fileRoots[fileRootIndex].GetPath());
					}

					if(removedFileListPath || removedConfigPath) {
						if(File.Exists(Mod.FileListPath.GetPath())) {
							File.Delete(Mod.FileListPath.GetPath());
						}

						if(File.Exists(Mod.ConfigPath.GetPath())) {
							File.Delete(Mod.ConfigPath.GetPath());
						}

						IO.CloseDirectory(Path.Combine(Paths.ModsPath.GetPath(), Mod.FileListPath.GetRelativePathTo(Paths.ModsPath).GetPath(1)));
					}
				} else {
					return true;
				}
			} catch (Exception e) {
				if(!Entry.Silent) {
					Error errorDialog = new Error(Localization.GetString("DeleteFilesFailure"), e.ToString());
					errorDialog.ShowDialog();
				}

				return false;
			}

			return true;
		}
	}
}
