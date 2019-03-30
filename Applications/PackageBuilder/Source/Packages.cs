using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using s4pi.Extensions;
using s4pi.Interfaces;
using s4pi.Package;
using s4pi.WrapperDealer;

namespace PackageBuilder {
	public static class Packages {
		public static Package OpenPackageStream (int apiVersion, Stream stream) {
			return (Package)Activator.CreateInstance(typeof(Package), BindingFlags.Instance | BindingFlags.NonPublic, null, new object[] { apiVersion, stream }, null);
		}

		public static void AddFiles (IPackage package, List<string> sourceFilePaths) {
			List<TGIN> addedResourceKeys = new List<TGIN>();

			for(int sourceFilePathIndex = 0; sourceFilePathIndex < sourceFilePaths.Count; sourceFilePathIndex++) {
				TGIN targetResourceKeyTGIN = Path.GetFileName(sourceFilePaths[sourceFilePathIndex]);
				AResourceKey targetResourceKey = targetResourceKeyTGIN;

				MemoryStream sourceStream = new MemoryStream();
				BinaryWriter sourceStreamWriter = new BinaryWriter(sourceStream);

				using(BinaryReader sourceFileReader = new BinaryReader(new FileStream(sourceFilePaths[sourceFilePathIndex], FileMode.Open, FileAccess.Read))) {
					sourceStreamWriter.Write(sourceFileReader.ReadBytes((int)sourceFileReader.BaseStream.Length));
					sourceStreamWriter.Flush();
				}

				IResourceIndexEntry targetPreviousEntry = package.Find(targetResourceKey.Equals);

				while(targetPreviousEntry != null) {
					package.DeleteResource(targetPreviousEntry);
					targetPreviousEntry = package.Find(targetResourceKey.Equals);
				}

				IResourceIndexEntry targetEntry = package.AddResource(targetResourceKey, sourceStream, false);

				if(targetEntry == null) {
					continue;
				}

				targetEntry.Compressed = 23106;
				addedResourceKeys.Add(targetResourceKeyTGIN);
			}

			GenerateNameMap(package, addedResourceKeys, null);
		}

		public static void RemoveFiles (IPackage package, List<string> fileNames) {
			List<TGIN> removedResourceKeys = new List<TGIN>();

			for(int fileNameIndex = 0; fileNameIndex < fileNames.Count; fileNameIndex++) {
				TGIN targetResourceKeyTGIN = fileNames[fileNameIndex];
				AResourceKey targetResourceKey = targetResourceKeyTGIN;

				IResourceIndexEntry targetPreviousEntry = package.Find(targetResourceKey.Equals);

				while(targetPreviousEntry != null) {
					package.DeleteResource(targetPreviousEntry);
					targetPreviousEntry = package.Find(targetResourceKey.Equals);
				}

				removedResourceKeys.Add(targetResourceKeyTGIN);
			}

			GenerateNameMap(package, null, removedResourceKeys);
		}

		public static void GenerateNameMap (IPackage package, List<TGIN> addedResourceKeys, List<TGIN> removedResourceKeys) {
			AResourceKey nameMapKey = new TGIBlock(0, null, 23462796u, 0u, 0uL);

			IResourceIndexEntry nameMapEntry = package.Find(nameMapKey.Equals);

			if(nameMapEntry == null) {
				nameMapEntry = package.AddResource(nameMapKey, null, false);
			}

			if(nameMapEntry != null) {
				NameMapResource.NameMapResource nameMapResource = (NameMapResource.NameMapResource)WrapperDealer.GetResource(0, package, nameMapEntry);

				if(nameMapResource == null || !typeof(IDictionary<ulong, string>).IsAssignableFrom(nameMapResource.GetType())) {
					package.DeleteResource(nameMapEntry);
					nameMapEntry = package.AddResource(nameMapKey, null, false);
					nameMapResource = (NameMapResource.NameMapResource)WrapperDealer.GetResource(0, package, nameMapEntry);
				}

				if(removedResourceKeys != null) {
					for(int removedResourceKeyIndex = 0; removedResourceKeyIndex < removedResourceKeys.Count; removedResourceKeyIndex++) {
						if(nameMapResource.Contains(removedResourceKeys[removedResourceKeyIndex].ResInstance)) {
							nameMapResource.Remove(removedResourceKeys[removedResourceKeyIndex].ResInstance);
						}
					}
				}

				if(addedResourceKeys != null) {
					for(int addedResourceKeyIndex = 0; addedResourceKeyIndex < addedResourceKeys.Count; addedResourceKeyIndex++) {
						if(addedResourceKeys[addedResourceKeyIndex].ResName == null) {
							continue;
						}

						if(nameMapResource.Contains(addedResourceKeys[addedResourceKeyIndex].ResInstance)) {
							nameMapResource[addedResourceKeys[addedResourceKeyIndex].ResInstance] = addedResourceKeys[addedResourceKeyIndex].ResName;
						} else {
							nameMapResource.Add(addedResourceKeys[addedResourceKeyIndex].ResInstance, addedResourceKeys[addedResourceKeyIndex].ResName);
						}
					}
				}

				List<KeyValuePair<ulong, string>> orderedNameMapResource = nameMapResource.ToList();
				orderedNameMapResource.Sort((pair1, pair2) => pair1.Value.CompareTo(pair2.Value));

				nameMapResource.Clear();

				for(int orderedNameMapResourceIndex = 0; orderedNameMapResourceIndex < orderedNameMapResource.Count; orderedNameMapResourceIndex++) {
					nameMapResource.Add(orderedNameMapResource[orderedNameMapResourceIndex].Key, orderedNameMapResource[orderedNameMapResourceIndex].Value);
				}

				package.ReplaceResource(nameMapEntry, nameMapResource);
			}
		}
	}
}
