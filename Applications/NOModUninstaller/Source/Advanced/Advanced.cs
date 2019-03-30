using System;
using System.IO;
using System.Windows.Forms;

namespace NOModUninstaller {
	public partial class Advanced : Form {
		public Advanced () {
			InitializeComponent();
		}

		private void Advanced_Load (object sender, EventArgs e) {
			UserDirectoryTextbox.Text = Paths.Sims4Path.GetPath();
		}

		private void UserDirectoryTextboxButton_Click (object sender, EventArgs e) {
			FolderBrowser.SelectedPath = UserDirectoryTextbox.Text;
			FolderBrowser.ShowDialog();
			UserDirectoryTextbox.Text = FolderBrowser.SelectedPath;
		}

		private void UninstallButton_Click (object sender, EventArgs e) {
			try {
				new DirectoryInfo(UserDirectoryTextbox.Text);
			} catch {
				MessageBox.Show(string.Format(Localization.GetString("InvalidDirectory"), UserDirectoryTextbox.Text));
				return;
			}

			Paths.Sims4Path = new IO.PathContainer(UserDirectoryTextbox.Text);

			Hide();
			Main.Run();
			Close();
		}

		private void AbortButton_Click (object sender, EventArgs e) {
			Close();
		}
	}
}
