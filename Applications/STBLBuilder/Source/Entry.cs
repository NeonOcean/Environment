using System;
using System.IO;

namespace STBLBuilder {
	public static class Entry {
		public static bool Completed {
			get; set;
		}

		public static bool PrintHelp {
			get; set;
		}

		public static bool CreateEmpty {
			get; set;
		}

		public static string TargetDirectoryPath {
			get; set;
		}

		public static string SourceFilePath {
			get; set;
		}

		static void Main () {
			AppDomain.CurrentDomain.ProcessExit += OnExit;

			try {
				if(!ReadArguments()) {
					Environment.ExitCode = 1;
					return;
				}

				STBLBuilder.Main.Run();
			} catch(Exception e) {
				Console.Error.WriteLine(e.ToString());
			}
		}

		private static void OnExit(object sender, EventArgs e) {
			if(!Completed) {
				if(Environment.ExitCode == 0) {
					Environment.ExitCode = 1;
				}
			} else {
				Environment.ExitCode = 0;
			}	
		}

		private static bool ReadArguments () {
			string[] arguments = Environment.GetCommandLineArgs();

			if(arguments.Length <= 1) {
				PrintHelp = true;
				return true;
			}

			for(int argumentIndex = 1; argumentIndex < arguments.Length; argumentIndex++) {
				if(arguments[argumentIndex].Equals("-?", StringComparison.OrdinalIgnoreCase) ||
					arguments[argumentIndex].Equals("/?", StringComparison.OrdinalIgnoreCase) ||
					arguments[argumentIndex].Equals("-h", StringComparison.OrdinalIgnoreCase) ||
					arguments[argumentIndex].Equals("/h", StringComparison.OrdinalIgnoreCase) ||
					arguments[argumentIndex].Equals("-help", StringComparison.OrdinalIgnoreCase) ||
					arguments[argumentIndex].Equals("/help", StringComparison.OrdinalIgnoreCase)) {
					PrintHelp = true;
					continue;
				}

				if(arguments[argumentIndex].Equals("-e", StringComparison.OrdinalIgnoreCase) ||
					arguments[argumentIndex].Equals("/e", StringComparison.OrdinalIgnoreCase)) {
					CreateEmpty = true;
					continue;
				}

				if(arguments[argumentIndex].Equals("-t", StringComparison.OrdinalIgnoreCase) ||
					arguments[argumentIndex].Equals("/t", StringComparison.OrdinalIgnoreCase)) {
					if(argumentIndex != arguments.Length - 1) {
						TargetDirectoryPath = arguments[argumentIndex + 1];
						argumentIndex++;
						continue;
					}
				}

				if(arguments[argumentIndex].Equals("-s", StringComparison.OrdinalIgnoreCase) ||
					arguments[argumentIndex].Equals("/s", StringComparison.OrdinalIgnoreCase)) {
					if(argumentIndex != arguments.Length - 1) {
						SourceFilePath = arguments[argumentIndex + 1];
						argumentIndex++;
						continue;
					}
				}
			}

			try {
				if(TargetDirectoryPath != null) {
					TargetDirectoryPath = Path.GetFullPath(TargetDirectoryPath);
					FileInfo targetFileInfo = new FileInfo(TargetDirectoryPath);
				} else {
					TargetDirectoryPath = Path.GetFullPath(".");
				}
			} catch (Exception e) {
				throw new Exception("Failed to parse argument '-t'", e);
			}

			try {
				if (SourceFilePath != null) {
					SourceFilePath = Path.GetFullPath(SourceFilePath);
					FileInfo sourceFileInfo = new FileInfo(SourceFilePath);

					if (!sourceFileInfo.Exists) {
						return false;
					}
				}
			} catch (Exception e) {
				throw new Exception("Failed to parse argument '-s'", e);
			}

			return true;
		}
	}
}
