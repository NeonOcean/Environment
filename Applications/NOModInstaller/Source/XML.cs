using System.IO;
using System.Xml;
using System.Xml.Serialization;

namespace NOModInstaller {
	public static class XML {
		public static object Read<T> (string serialized) {
			using(StringReader Reader = new StringReader(serialized)) {
				return new XmlSerializer(typeof(T)).Deserialize(Reader);
			}
		}
	}
}
