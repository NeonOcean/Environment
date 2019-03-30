using System;
using System.Windows.Forms;

namespace NOModInstaller {
	public partial class Error : Form {
		public Error (string message, string errorInformation) {
			InitializeComponent();

			MessageText.Text = message;
			ErrorTextBox.Text = errorInformation;
		}

		private void OkButton_Click (object sender, EventArgs e) {
			Close();
		}
	}
}
