using Microsoft.Win32;
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Diagnostics;
using System.IO;
using System.IO.Compression;
using System.Windows.Forms;

namespace NOModInstaller {
	public static class Main {
		private static Func<bool>[] phases = new Func<bool>[] {
			CheckGame, ExtractModFiles, Uninstall, MoveModFiles, EnableMods, CleanUp
		};

		public static bool Run () {
			if(Paths.Sims4Path == null) {
				if(!Entry.Silent) {
					Abort abortMenu = new Abort();
					abortMenu.ShowDialog();
				}

				return false;
			}

			if(!Entry.Silent) {
				ProgressBar progressBarMenu = new ProgressBar();
				progressBarMenu.StartBackgroundWorker(Install);
				progressBarMenu.ShowDialog();

				if(!progressBarMenu.Completed) {
					Abort abortMenu = new Abort();
					abortMenu.ShowDialog();

					return false;
				}
			} else {
				if(!Install(null)) {
					return false;
				}
			}

			if(!Entry.Quick && !Entry.Silent) {
				Completion completionMenu = new Completion();
				completionMenu.ShowDialog();
			}

			Entry.Completed = true;
			return true;
		}

		private static bool Install (Action<int, string> phaseCallback) {
			for(int phaseIndex = 0; phaseIndex < phases.Length; phaseIndex++) {
				if(phaseCallback != null) {
					phaseCallback.Invoke(100 / phases.Length * (phaseIndex), "Phase" + phases[phaseIndex].Method.Name + "Text");
				}

				if(!phases[phaseIndex].Invoke()) {
					return false;
				}
			}

			if(phaseCallback != null) {
				phaseCallback.Invoke(100, "InstallationCompletePhaseText");
			}

			return true;
		}

		private static bool Install (BackgroundWorker backgroundWorker, DoWorkEventArgs eventArgs) {
			for(int phaseIndex = 0; phaseIndex < phases.Length; phaseIndex++) {
				backgroundWorker.ReportProgress(100 / phases.Length * (phaseIndex), "Phase" + phases[phaseIndex].Method.Name + "Text");

				if(!phases[phaseIndex].Invoke()) {
					return false;
				}
			}

			backgroundWorker.ReportProgress(100, "InstallationCompletePhaseText");

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
					MessageBox.Show(Localization.GetString("Sims4RunningText"));
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

		private static bool ExtractModFiles () {
			try {
				string extractionPath = Path.Combine(Paths.TemporaryPath.GetPath(), "Extracted");

				using(ZipArchive modFilesArchive = Mod.GetFilesArchive()) {
					if(Directory.Exists(extractionPath)) {
						Directory.Delete(extractionPath, true);
					}

					Directory.CreateDirectory(extractionPath);
					modFilesArchive.ExtractToDirectory(extractionPath);
				}
			} catch(Exception e) {
				if(!Entry.Silent) {
					Error errorDialog = new Error(Localization.GetString("ExtractionFailure"), e.ToString());
					errorDialog.ShowDialog();
				}

				return false;
			}

			return true;
		}

		private static bool Uninstall () {
			foreach(IO.PathContainer uninstallerPath in Mod.GetValidUninstallerPaths()) {
				if(!UninstallApplication(uninstallerPath)) {
					return false;
				}
			}

			if(!UninstallAntique()) {
				return false;
			}

			if(!UninstallCleanupUniqueFiles()) {
				return false;
			}

			return true;
		}

		private static bool UninstallApplication (IO.PathContainer uninstallerPath) {
			try {
				using(Process uninstallProcess = new Process() {
					StartInfo = {
						FileName = uninstallerPath.GetPath(),
						Arguments = "-q " + (Entry.Silent ? "-s " : " ") + "-p -t \"" + Paths.Sims4Path + "\"",
					}
				}) {
					uninstallProcess.Start();
					uninstallProcess.WaitForExit();

					if(uninstallProcess.ExitCode == 1) {
						return false;
					}

					if(File.Exists(uninstallerPath.GetPath())) {
						File.Delete(uninstallerPath.GetPath());
					}

					IO.CloseDirectory(Path.Combine(Paths.ModsPath.GetPath(), uninstallerPath.GetRelativePathTo(Paths.ModsPath).GetPath(1)));
				}
			} catch(Exception e) {
				if(!Entry.Silent) {
					Error errorDialog = new Error(Localization.GetString("UninstallFailure"), e.ToString());
					errorDialog.ShowDialog();
				}

				return false;
			}

			return true;
		}

		private static bool UninstallAntique () {
			IO.PathContainer identifyingFile = null;
			string version = null;

			try {
				identifyingFile = Antique.GetIdentifyingFile();
				version = Antique.GetVersion();
			} catch(Exception e) {
				if(!Entry.Silent) {
					Error errorDialog = new Error(Localization.GetString("UninstallAntiqueReadVersionFailure"), e.ToString());
					errorDialog.ShowDialog();
				}

				return false;
			}

			try {
				if(version != null) {
					List<IO.PathContainer> files = null;

					foreach(Mod.AntiqueFileList antiqueFileList in Mod.AntiqueFileLists) {
						if(antiqueFileList.Version == version) {
							files = antiqueFileList.GetFilesFullPaths();
						}
					}

					if(files != null) {
						List<IO.PathContainer> fileRoots = new List<IO.PathContainer>();

						bool removedIdentifyingFile = false;

						for(int fileIndex = 0; fileIndex < files.Count; fileIndex++) {
							if(files[fileIndex].Equals(identifyingFile)) {
								files.RemoveAt(fileIndex);
								fileIndex--;
								removedIdentifyingFile = true;
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

						if(removedIdentifyingFile) {
							if(File.Exists(identifyingFile.GetPath())) {
								File.Delete(identifyingFile.GetPath());
							}

							IO.CloseDirectory(Path.Combine(Paths.ModsPath.GetPath(), identifyingFile.GetRelativePathTo(Paths.ModsPath).GetPath(1)));
						}
					} else {
						if(!Entry.Silent) {
							string errorMessage = Localization.GetString("UninstallAntiqueUnknownVersionFailure");
							Error errorDialog = new Error(errorMessage, errorMessage);
							errorDialog.ShowDialog();
						}

						return false;
					}
				}
			} catch(Exception e) {
				if(!Entry.Silent) {
					Error errorDialog = new Error(Localization.GetString("UninstallAntiqueDeleteFailure"), e.ToString());
					errorDialog.ShowDialog();
				}

				return false;
			}

			return true;
		}

		private static bool UninstallCleanupUniqueFiles () {
			try {
				IO.DeleteFiles(Mod.GetValidUniqueFilePaths());
			} catch(Exception e) {
				if(!Entry.Silent) {
					Error errorDialog = new Error(Localization.GetString("UninstallUnqiueFileCleanupFailure"), e.ToString());
					errorDialog.ShowDialog();
				}

				return false;
			}

			return true;
		}

		private static bool MoveModFiles () {
			try {
				Directory.CreateDirectory(Paths.ModsPath.GetPath());
				IO.MoveDirectory(Path.Combine(Paths.TemporaryPath.GetPath(), "Extracted"), Paths.ModsPath.GetPath());
			} catch(Exception e) {
				if(!Entry.Silent) {
					Error errorDialog = new Error(Localization.GetString("MoveFilesFailure"), e.ToString());
					errorDialog.ShowDialog();
				}

				return false;
			}

			return true;
		}

		private static bool EnableMods () {
			string sims4OptionsPath = Paths.Sims4OptionsPath.GetPath();

			if(!File.Exists(sims4OptionsPath) || Entry.Silent) {
				return true;
			}

			try {
				string modsDisabledValue = INI.Read("options", "modsdisabled", sims4OptionsPath);
				string scriptModsEnabledValue = INI.Read("options", "scriptmodsenabled", sims4OptionsPath);

				bool changeValues = false;

				if(modsDisabledValue != "0") {
					if(!changeValues) {
						DialogResult result = MessageBox.Show(Localization.GetString("EnableModsPrompt"), "", MessageBoxButtons.YesNo);
						if(result == DialogResult.No) {
							return true;
						}

						changeValues = true;
						INI.Write("options", "modsdisabled", "0", sims4OptionsPath);
					} else {
						INI.Write("options", "modsdisabled", "0", sims4OptionsPath);
					}
				}

				if(scriptModsEnabledValue != "1") {
					if(!changeValues) {
						DialogResult result = MessageBox.Show(Localization.GetString("EnableModsPrompt"), "", MessageBoxButtons.YesNo);
						if(result == DialogResult.No) {
							return true;
						}

						changeValues = true;
						INI.Write("options", "scriptmodsenabled", "1", Paths.Sims4OptionsPath.GetPath());
					} else {
						INI.Write("options", "scriptmodsenabled", "1", Paths.Sims4OptionsPath.GetPath());
					}
				}
			} catch(Exception e) {
				if(!Entry.Silent) {
					Error errorDialog = new Error(Localization.GetString("EnableModsFailure"), e.ToString());
					errorDialog.ShowDialog();
				}

				return true;
			}

			return true;
		}

		private static bool CleanUp () {
			try {
				Directory.Delete(Paths.TemporaryPath.GetPath(), true);
			} catch(Exception e) {
				if(!Entry.Silent) {
					Error errorDialog = new Error(Localization.GetString("CleanUpFailure"), e.ToString());
					errorDialog.ShowDialog();
				}

				return false;
			}

			return true;
		}
	}
}