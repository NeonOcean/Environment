using System;
using System.Windows.Forms;

namespace NOModInstaller {
	public partial class Setup : Form {
		public Setup () {
			InitializeComponent();
		}

		private void Setup_Load (object sender, EventArgs e) {
			Text = string.Format(Text, Mod.Name);
			InformationText.Text = string.Format(InformationText.Text, Mod.Name);
		}

		private void AdvancedButton_Click (object sender, EventArgs e) {
			Advanced advancedMenu = new Advanced();

			Hide();
			advancedMenu.ShowDialog();
			Close();
		}

		private void InstallButton_Click (object sender, EventArgs e) {
			Hide();

			if(Paths.Sims4Path == null) {
				Advanced advancedMenu = new Advanced();

				Hide();

				MessageBox.Show(Localization.GetString("CouldNotFindSims4DirectoryMessageText"), "", MessageBoxButtons.OK, MessageBoxIcon.Exclamation);
				advancedMenu.ShowDialog();		

				Close();
			}

			Main.Run();
			Close();
		}

		private void AbortButton_Click (object sender, EventArgs e) {
			Close();
		}
	}
}
