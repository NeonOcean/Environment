namespace NOModUninstaller {
	partial class ProgressBar {
		/// <summary>
		/// Required designer variable.
		/// </summary>
		private System.ComponentModel.IContainer components = null;

		/// <summary>
		/// Clean up any resources being used.
		/// </summary>
		/// <param name="disposing">true if managed resources should be disposed; otherwise, false.</param>
		protected override void Dispose (bool disposing) {
			if(disposing && (components != null)) {
				components.Dispose();
			}
			base.Dispose(disposing);
		}

		#region Windows Form Designer generated code

		/// <summary>
		/// Required method for Designer support - do not modify
		/// the contents of this method with the code editor.
		/// </summary>
		private void InitializeComponent () {
			System.ComponentModel.ComponentResourceManager resources = new System.ComponentModel.ComponentResourceManager(typeof(ProgressBar));
			this.DeinstallationProgressBar = new System.Windows.Forms.ProgressBar();
			this.PhaseText = new System.Windows.Forms.Label();
			this.PhaseTextPanel = new System.Windows.Forms.Panel();
			this.DeinstallationBackgroundWorker = new System.ComponentModel.BackgroundWorker();
			this.PhaseTextPanel.SuspendLayout();
			this.SuspendLayout();
			// 
			// DeinstallationProgressBar
			// 
			resources.ApplyResources(this.DeinstallationProgressBar, "DeinstallationProgressBar");
			this.DeinstallationProgressBar.Name = "DeinstallationProgressBar";
			// 
			// PhaseText
			// 
			resources.ApplyResources(this.PhaseText, "PhaseText");
			this.PhaseText.Name = "PhaseText";
			// 
			// PhaseTextPanel
			// 
			this.PhaseTextPanel.Controls.Add(this.PhaseText);
			resources.ApplyResources(this.PhaseTextPanel, "PhaseTextPanel");
			this.PhaseTextPanel.Name = "PhaseTextPanel";
			// 
			// DeinstallationBackgroundWorker
			// 
			this.DeinstallationBackgroundWorker.WorkerReportsProgress = true;
			this.DeinstallationBackgroundWorker.DoWork += new System.ComponentModel.DoWorkEventHandler(this.DeinstallationBackgroundWorker_DoWork);
			this.DeinstallationBackgroundWorker.ProgressChanged += new System.ComponentModel.ProgressChangedEventHandler(this.DeinstallationBackgroundWorker_ProgressChanged);
			this.DeinstallationBackgroundWorker.RunWorkerCompleted += new System.ComponentModel.RunWorkerCompletedEventHandler(this.DeinstallationBackgroundWorker_RunWorkerCompleted);
			// 
			// ProgressBar
			// 
			resources.ApplyResources(this, "$this");
			this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
			this.ControlBox = false;
			this.Controls.Add(this.PhaseTextPanel);
			this.Controls.Add(this.DeinstallationProgressBar);
			this.FormBorderStyle = System.Windows.Forms.FormBorderStyle.FixedSingle;
			this.MaximizeBox = false;
			this.MinimizeBox = false;
			this.Name = "ProgressBar";
			this.ShowIcon = false;
			this.PhaseTextPanel.ResumeLayout(false);
			this.ResumeLayout(false);

		}

		#endregion

		private System.Windows.Forms.ProgressBar DeinstallationProgressBar;
		private System.Windows.Forms.Label PhaseText;
		private System.Windows.Forms.Panel PhaseTextPanel;
		private System.ComponentModel.BackgroundWorker DeinstallationBackgroundWorker;
	}
}