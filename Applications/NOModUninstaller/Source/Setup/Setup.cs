using System;
using System.Windows.Forms;

namespace NOModUninstaller {
	public partial class Setup : Form {
		public Setup () {
			InitializeComponent();
		}

		private void Setup_Load (object sender, EventArgs e) {
			Text = string.Format(Text, Mod.ModName);
			InformationText.Text = string.Format(InformationText.Text, Mod.ModName);
		}

		private void AdvancedButton_Click (object sender, EventArgs e) {
			Advanced advancedMenu = new Advanced();

			Hide();
			advancedMenu.ShowDialog();
			Close();
		}

		private void UninstallButton_Click (object sender, EventArgs e) {
			Hide();
			Main.Run();
			Close();
		}

		private void AbortButton_Click (object sender, EventArgs e) {
			Close();
		}
	}
}
