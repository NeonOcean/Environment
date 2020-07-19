using System;
using System.Windows.Forms;

namespace NOModInstaller {
	public partial class Completion : Form {
		public Completion () {
			InitializeComponent();
		}

		private void Completion_Load (object sender, EventArgs e) {
			Text = string.Format(Text, Mod.Name);
			CompletionInformation.Text = string.Format(CompletionInformation.Text, Mod.Name);
		}

		private void FinishButton_Click (object sender, EventArgs e) {
			Close();
		}
	}
}