using System;
using System.Text;
using System.Diagnostics;
using System.Runtime.InteropServices;
using System.ComponentModel;

namespace NOModInstaller {
	public class Processes {
		public static string GetPath (Process Process) {
			if(Environment.OSVersion.Version.Major >= 6) {
				StringBuilder output = new StringBuilder(1024);
				IntPtr processHandle = OpenProcess(0x1000, false, Process.Id);

				if(processHandle != IntPtr.Zero) {
					try {
						int outputCapacity = output.Capacity;
						if(QueryFullProcessImageName(processHandle, 0, output, out outputCapacity)) {
							return output.ToString();
						}
					} finally {
						CloseHandle(processHandle);
					}
				}

				throw new Win32Exception(Marshal.GetLastWin32Error());
			} else {
				return Process.MainModule.FileName;
			}
		}

		[DllImport("kernel32.dll")]
		private static extern bool QueryFullProcessImageName (IntPtr processHandle, int flags, StringBuilder output, out int outputCapacity);
		[DllImport("kernel32.dll")]
		private static extern IntPtr OpenProcess (uint desiredAccess, bool inheritHandle, int processId);
		[DllImport("kernel32.dll", SetLastError = true)]
		private static extern bool CloseHandle (IntPtr handle);
	}
}
