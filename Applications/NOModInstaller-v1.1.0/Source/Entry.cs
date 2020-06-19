using System;
using System.IO;
using System.Windows.Forms;

namespace NOModInstaller {
	public static class Entry {
		public static string Namespace {
			get; private set;
		}

		public static bool Completed {
			get; set;
		}

		public static bool Quick {
			get; private set;
		}

		public static bool Silent {
			get; private set;
		}

		public static string Target {
			get; private set;
		}

		[STAThread]
		static void Main () {
			AppDomain.CurrentDomain.ProcessExit += OnExit;

			Namespace = "NOModInstaller";

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

			NOModInstaller.Main.Run();
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
						new DirectoryInfo(Target);
					} catch {
						if(!Silent) {
							MessageBox.Show(string.Format(Localization.GetString("InvalidDirectory"), Target));
						}

						return false;
					}
				}

				return true;
			} catch (Exception e) {
				throw new Exception("Failed to parse argument '-t'", e);
			}
		}
	}
}
