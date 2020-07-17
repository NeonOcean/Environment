using System;
using System.IO;
using System.Windows.Forms;

namespace NOModInstaller {
	public partial class Advanced : Form {
		public Advanced () {
			InitializeComponent();
		}

		private void Advanced_Load (object sender, EventArgs e) {
			if(Paths.Sims4Path == null) {
				UserDirectoryTextbox.Text = "";
			} else {
				UserDirectoryTextbox.Text = Paths.Sims4Path.GetPath();
			}
		}

		private void UserDirectoryTextboxButton_Click (object sender, EventArgs e) {
			FolderBrowser.SelectedPath = UserDirectoryTextbox.Text;
			FolderBrowser.ShowDialog();
			UserDirectoryTextbox.Text = FolderBrowser.SelectedPath;
		}

		private void UserDirectoryTextbox_TextChanged (object sender, EventArgs e) {
			if(UserDirectoryTextbox.Text != "") {
				ModsDirectoryTextbox.Text = Path.Combine(UserDirectoryTextbox.Text, "Mods");
			} else {
				ModsDirectoryTextbox.Text = "/Mods";
			}
		}

		private void InstallButton_Click (object sender, EventArgs e) {
			try {
				new DirectoryInfo(UserDirectoryTextbox.Text);
			} catch {
				MessageBox.Show(string.Format(Localization.GetString("InvalidDirectory"), UserDirectoryTextbox.Text));
				return;
			}

			IO.PathContainer sims4Path = new IO.PathContainer(UserDirectoryTextbox.Text);
			string[] sims4PathSegments = sims4Path.GetSegments();

			if(sims4PathSegments.Length >= 2) {
				if(sims4PathSegments[sims4PathSegments.Length - 1].ToLower() == "mods") {
					if(MessageBox.Show(Localization.GetString("SelectedModsFolderMessageText"), "", MessageBoxButtons.YesNo, MessageBoxIcon.Exclamation) != DialogResult.Yes) {
						return;
					}
				}
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
