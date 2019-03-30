using System;
using System.Collections.Generic;
using System.IO;
using System.Text;
using System.Xml.Serialization;

namespace STBLBuilder {
	public static class STBL {
		public const string STBLFilePrefix = "S4_220557DA_";
		public const string STBLFileSuffix = "%%+STBL";
		public const string STBLFileExtension = "stbl";

		public static readonly Dictionary<string, string> Languages = new Dictionary<string, string>() {
			["English"] = "00",
			["Chinese_Simplified"] = "01",
			["Chinese_Traditional"] = "02",
			["Czech"] = "03",
			["Danish"] = "04",
			["Dutch"] = "05",
			["Finnish"] = "06",
			["French"] = "07",
			["German"] = "08",
			["Greek"] = "09",
			["Hungarian"] = "0A",
			["Italian"] = "0B",
			["Japanese"] = "0C",
			["Korean"] = "0D",
			["Norwegian"] = "0E",
			["Polish"] = "0F",
			["Portuguese_Portugal"] = "10",
			["Portuguese_Brazil"] = "11",
			["Russian"] = "12",
			["Spanish_Spain"] = "13",
			["Spanish_Mexico"] = "14",
			["Swedish"] = "15",
			["Thai"] = "16"
		};

		public static File ReadXMLSourceFile (string sourcePath) {
			if(!System.IO.File.Exists(sourcePath)) {
				throw new FileNotFoundException("File does not exist.");
			}

			File file = null;

			try {
				file = (File)Tools.ReadXML<File>(sourcePath);
			} catch(Exception e) {
				throw new Exception("Failed to read language source file.", e);
			}

			if(file.Group.StartsWith("0x", StringComparison.OrdinalIgnoreCase)) {
				throw new Exception("Group id should not be prefixed with '0x'.");
			}

			if(file.Group.Length != 8) {
				throw new Exception("Group id needs to be 16 characters long.");
			}

			if(file.Instance.StartsWith("0x", StringComparison.OrdinalIgnoreCase)) {
				throw new Exception("Instance id should not be prefixed with '0x'.");
			}

			if(file.Instance.Length != 16) {
				throw new Exception("Instance id needs to be 16 characters long.");
			}

			if(!file.Name.Contains("{0}")) {
				throw new Exception("File name should contain '{0}' to be replaced with the name of the language being built.");
			}

			for(int entryIndex = 0; entryIndex < file.Entries.Length; entryIndex++) {
				if(file.Entries[entryIndex].Key == 0) {
					throw new Exception("Key number '" + file.Entries[entryIndex].Key + "' cannot be zero");
				}

				for(int comparingEntryIndex = 0; comparingEntryIndex < file.Entries.Length; comparingEntryIndex++) {
					if(entryIndex != comparingEntryIndex && file.Entries[entryIndex].Key == file.Entries[comparingEntryIndex].Key) {
						throw new Exception("Duplicate key found for '" + file.Entries[comparingEntryIndex].Key + "'.");
					}
				}
			}

			return file;
		}

		public static void Build (string sourcePath, string buildPath) {
			File file = null;
			file = ReadXMLSourceFile(sourcePath);
			Build(file, buildPath);
		}

		public static void Build (File file, string buildPath) {
			Directory.CreateDirectory(buildPath);

			foreach(KeyValuePair<string, string> language in Languages) {
				string sourceFileName = STBLFilePrefix + file.Group + "_" + language.Value + file.Instance.Substring(2) + "_" + String.Format(file.Name, language.Key) + STBLFileSuffix + "." + STBLFileExtension;
				string sourcePath = Path.Combine(buildPath, sourceFileName);

				using(BinaryWriter writer = new BinaryWriter(new FileStream(sourcePath, FileMode.Create))) {
					string[] texts = new string[file.Entries.Length];
					ushort[] textsByteCounts = new ushort[file.Entries.Length];
					uint entryByteCount = 0;

					for(int textsIndex = 0; textsIndex < file.Entries.Length; textsIndex++) {
						texts[textsIndex] = file.Entries[textsIndex].GetText(language.Key);

						if(file.Entries[textsIndex].English != null) {
							texts[textsIndex] = file.Entries[textsIndex].English;
						} else {
							texts[textsIndex] = file.Entries[textsIndex].Identifier;
						}

						textsByteCounts[textsIndex] = (ushort)Encoding.UTF8.GetByteCount(texts[textsIndex]);
						entryByteCount += textsByteCounts[textsIndex] + 1u;
					}

					writer.Write(Encoding.UTF8.GetBytes("STBL"));
					writer.Write((byte)5);
					writer.Write((ushort)0);
					writer.Write((uint)file.Entries.Length);
					writer.Write(0u);
					writer.Write((ushort)0);
					writer.Write(entryByteCount);

					for(int textsIndex = 0; textsIndex < file.Entries.Length; textsIndex++) {
						writer.Write(file.Entries[textsIndex].Key);
						writer.Write((byte)0);
						writer.Write(textsByteCounts[textsIndex]);
						writer.Write(texts[textsIndex].ToCharArray());
					}
				}
			}
		}

		public static void CreateEmpty (string filePath) {
			Tools.WriteXML(filePath, new File() {
				Entries = new Entry[] {
					new Entry() {
						Identifier = "STBLBuilderValueExample",
						Key = 52,
						English = "This is an example STBL value."
					},

					new Entry()
				}
			});
		}

		public class File {
			public string Group {
				get; set;
			} = "";

			public string Instance {
				get; set;
			} = "";

			public string Name {
				get; set;
			} = "";

			public Entry[] Entries {
				get; set;
			} = new Entry[0];
		}

		public class Entry {
			public string Identifier {
				get; set;
			} = "";

			public UInt32 Key {
				get; set;
			} = 0;

			[XmlElement(IsNullable = true)]
			public string English {
				get; set;
			} = null;

			[XmlElement(IsNullable = true)]
			public string ChineseSimplified {
				get; set;
			} = null;

			[XmlElement(IsNullable = true)]
			public string ChineseTraditional {
				get; set;
			} = null;

			[XmlElement(IsNullable = true)]
			public string Czech {
				get; set;
			} = null;

			[XmlElement(IsNullable = true)]
			public string Danish {
				get; set;
			} = null;

			[XmlElement(IsNullable = true)]
			public string Dutch {
				get; set;
			} = null;

			[XmlElement(IsNullable = true)]
			public string Finnish {
				get; set;
			} = null;

			[XmlElement(IsNullable = true)]
			public string French {
				get; set;
			} = null;

			[XmlElement(IsNullable = true)]
			public string German {
				get; set;
			} = null;

			[XmlElement(IsNullable = true)]
			public string Greek {
				get; set;
			} = null;

			[XmlElement(IsNullable = true)]
			public string Hungarian {
				get; set;
			} = null;

			[XmlElement(IsNullable = true)]
			public string Italian {
				get; set;
			} = null;

			[XmlElement(IsNullable = true)]
			public string Japanese {
				get; set;
			} = null;

			[XmlElement(IsNullable = true)]
			public string Korean {
				get; set;
			} = null;

			[XmlElement(IsNullable = true)]
			public string Norwegian {
				get; set;
			} = null;

			[XmlElement(IsNullable = true)]
			public string Polish {
				get; set;
			} = null;

			[XmlElement(IsNullable = true)]
			public string PortuguesePortugal {
				get; set;
			} = null;

			[XmlElement(IsNullable = true)]
			public string PortugueseBrazil {
				get; set;
			} = null;

			[XmlElement(IsNullable = true)]
			public string Russian {
				get; set;
			} = null;

			[XmlElement(IsNullable = true)]
			public string SpanishSpain {
				get; set;
			} = null;

			[XmlElement(IsNullable = true)]
			public string SpanishMexico {
				get; set;
			} = null;

			[XmlElement(IsNullable = true)]
			public string Swedish {
				get; set;
			} = null;

			[XmlElement(IsNullable = true)]
			public string Thai {
				get; set;
			} = null;

			public string GetText (string Language) {
				switch(Language) {
					case "English":
						return English;
					case "Chinese_Simplified":
						return ChineseSimplified;
					case "Chinese_Traditional":
						return ChineseTraditional;
					case "Czech":
						return Czech;
					case "Danish":
						return Danish;
					case "Dutch":
						return Dutch;
					case "Finnish":
						return Finnish;
					case "French":
						return French;
					case "German":
						return German;
					case "Greek":
						return Greek;
					case "Hungarian":
						return Hungarian;
					case "Italian":
						return Italian;
					case "Japanese":
						return Japanese;
					case "Korean":
						return Korean;
					case "Norwegian":
						return Norwegian;
					case "Polish":
						return Polish;
					case "Portuguese_Brazil":
						return PortugueseBrazil;
					case "Portuguese_Portugal":
						return PortuguesePortugal;
					case "Russian":
						return Russian;
					case "Spanish_Mexico":
						return SpanishMexico;
					case "Spanish_Spain":
						return SpanishSpain;
					case "Swedish":
						return Swedish;
					case "Thai":
						return Thai;
					default:
						throw new ArgumentException("'" + Language + "' is not a valid language");
				}
			}
		}
	}
}
