using System;
using System.ComponentModel;
using System.Windows.Forms;

namespace NOModInstaller {
	public partial class ProgressBar : Form {
		public bool Completed = false;

		public ProgressBar () {
			InitializeComponent();
		}

		public void StartBackgroundWorker (Func<BackgroundWorker, DoWorkEventArgs, bool> thread) {
			InstallationBackgroundWorker.RunWorkerAsync(thread);
		}

		private void InstallationBackgroundWorker_DoWork (object sender, DoWorkEventArgs e) {
			e.Result = ((Func<BackgroundWorker, DoWorkEventArgs, bool>)e.Argument).Invoke((BackgroundWorker)sender, e);
		}

		private void InstallationBackgroundWorker_ProgressChanged (object sender, ProgressChangedEventArgs e) {
			InstallationProgressBar.Value = e.ProgressPercentage;
			PhaseText.Text = Localization.GetString((string)e.UserState);
		}

		private void InstallationBackgroundWorker_RunWorkerCompleted (object sender, RunWorkerCompletedEventArgs e) {
			Completed = (bool)e.Result;
			Close();
		}
	}
}
