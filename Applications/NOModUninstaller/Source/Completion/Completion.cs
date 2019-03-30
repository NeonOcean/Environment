using System;
using System.Windows.Forms;

namespace NOModUninstaller {
	public partial class Completion : Form {
		public Completion () {
			InitializeComponent();
		}

		private void FinishButton_Click (object sender, EventArgs e) {
			Close();
		}
	}
}
