using System;
using System.ComponentModel;
using System.Windows.Forms;

namespace NOModUninstaller {
	public partial class ProgressBar : Form {
		public bool Completed = false;

		public ProgressBar () {
			InitializeComponent();
		}

		public void StartBackgroundWorker (Func<BackgroundWorker, DoWorkEventArgs, bool> thread) {
			DeinstallationBackgroundWorker.RunWorkerAsync(thread);
		}

		private void DeinstallationBackgroundWorker_DoWork (object sender, DoWorkEventArgs e) {
			e.Result = ((Func<BackgroundWorker, DoWorkEventArgs, bool>)e.Argument).Invoke((BackgroundWorker)sender, e);
		}

		private void DeinstallationBackgroundWorker_ProgressChanged (object sender, ProgressChangedEventArgs e) {
			DeinstallationProgressBar.Value = e.ProgressPercentage;
			PhaseText.Text = Localization.GetString((string)e.UserState);
		}

		private void DeinstallationBackgroundWorker_RunWorkerCompleted (object sender, RunWorkerCompletedEventArgs e) {
			Completed = (bool)e.Result;
			Close();
		}
	}
}
