using System;
using System.Text.RegularExpressions;

namespace NOModInstaller {
	public static class Tools {
		public static string NormalizeLineEndings (string abnormalString) {
			if(abnormalString == null) {
				return abnormalString;
			}

			return NormalizeLineEndings(abnormalString, Environment.NewLine);
		}

		public static string NormalizeLineEndings (string abnormalString, string correctLineEnding) {
			if(abnormalString == null) {
				return abnormalString;
			}

			return Regex.Replace(abnormalString, @"\r\n|\r|\n", correctLineEnding);
		}
	}
}
