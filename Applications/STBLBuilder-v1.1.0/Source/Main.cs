using System;
using System.Diagnostics;
using System.IO;

namespace STBLBuilder {
	public static class Main {
		public static bool Run () {
			if(Entry.PrintHelp) {
				PrintHelp();
			}

			if(Entry.CreateEmpty) {
				STBL.CreateEmpty(Path.Combine(Path.GetDirectoryName(Process.GetCurrentProcess().MainModule.FileName), "Empty.xml"));
			}

			if(Entry.SourceFilePath == null) {
				Console.Error.WriteLine("No source files where specified");
				return false;
			}

			STBL.File sourceFile = STBL.ReadXMLSourceFile(Entry.SourceFilePath);

			if(Entry.TargetDirectoryPath != null) {
				STBL.Build(sourceFile, Entry.TargetDirectoryPath);
			}

			Entry.Completed = true;
			return true;
		}

		public static void PrintHelp () {
			Console.WriteLine(
				"Builds a Sims 4 STBL file from xml sources. \n" +
				"\n" +
				Path.GetFileNameWithoutExtension(Process.GetCurrentProcess().MainModule.FileName) + " [-h] [-e] [-t[filepath]] [-s[filepath] [-p] \n" +
				"\n" +
				" -h\t\t\tPrints this help message. \n" +
				"\n" +
				" -e\t\t\tCreates an empty xml source file called empty.xml \n" +
				"\t\t\twhich will be found in the same directory as \n" +
				"\t\t\tthis application. \n" +
				"\n" +
				" -t [directorypath]\tDesignates the directory path the STBL file will \n" +
				"\t\t\tbe saved to. The path can be relative to the \n" +
				"\t\t\tworking directory. \n" +
				"\n" +
				" -s [filepath]\t\tDesignates the source file path. The source file's \n" +
				"\t\t\tThe path can be relative to the working directory. \n" +
				"\n" +
				" -p\t\t\tWith this argument, this tool will create source \n" +
				"\t\t\tinfo files for use with the PackageBuilder tool. \n");
		}
	}
}
