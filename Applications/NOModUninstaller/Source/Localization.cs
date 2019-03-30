using System.Globalization;
using System.Reflection;
using System.Resources;

namespace NOModUninstaller {
	public static class Localization {
		public static ResourceManager Manager {
			get; private set;
		} 

		static Localization () {
			Manager = new ResourceManager(Entry.Namespace + ".Resources.Strings", Assembly.GetExecutingAssembly());
		}

		public static string GetString (string name) {
			return Manager.GetString(name);
		}

		public static string GetString (string name, CultureInfo culture) {
			return Manager.GetString(name, culture);
		}
	}
}
