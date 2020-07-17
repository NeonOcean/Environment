using System.Text;
using System.Runtime.InteropServices;

namespace NOModInstaller {
	public static class INI {
		public static string Read (string section, string key, string filePath) {
			return Read(section, key, "", filePath);
		}

		public static string Read (string section, string key, string defaultValue, string filePath) {
			StringBuilder returnValue = new StringBuilder(255);
			GetPrivateProfileString(section, key, defaultValue, returnValue, returnValue.Capacity, filePath);
			return returnValue.ToString();
		}

		public static void Write (string section, string key, string value, string filePath) {
			WritePrivateProfileString(section, key, value, filePath);
		}

		[DllImport("kernel32")]
		private static extern long WritePrivateProfileString (string section, string key, string value, string filePath);
		[DllImport("kernel32")]
		private static extern int GetPrivateProfileString (string section, string key, string defaultValue, StringBuilder returnValue, int returnSize, string filePath);
	}
}
