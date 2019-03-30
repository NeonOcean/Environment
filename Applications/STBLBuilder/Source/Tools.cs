using System;
using System.IO;
using System.Xml;
using System.Xml.Serialization;

namespace STBLBuilder {
	public static class Tools {
		public static object ReadXML<T> (string file) {
			using(XmlTextReader reader = new XmlTextReader(file)) {
				return new XmlSerializer(typeof(T)).Deserialize(reader);
			}
		}

		public static void WriteXML (string file, object target) {
			Directory.CreateDirectory(Path.GetDirectoryName(file));

			using(XmlWriter writer = XmlWriter.Create(file, new XmlWriterSettings() { Indent = true, IndentChars = "\t" })) {
				new XmlSerializer(target.GetType()).Serialize(writer, target);
			}
		}
	}
}
