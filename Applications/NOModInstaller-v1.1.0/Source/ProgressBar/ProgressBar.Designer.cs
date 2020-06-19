namespace NOModInstaller {
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
			this.InstallationProgressBar = new System.Windows.Forms.ProgressBar();
			this.PhaseText = new System.Windows.Forms.Label();
			this.PhaseTextPanel = new System.Windows.Forms.Panel();
			this.InstallationBackgroundWorker = new System.ComponentModel.BackgroundWorker();
			this.PhaseTextPanel.SuspendLayout();
			this.SuspendLayout();
			// 
			// InstallationProgressBar
			// 
			this.InstallationProgressBar.Location = new System.Drawing.Point(12, 12);
			this.InstallationProgressBar.Name = "InstallationProgressBar";
			this.InstallationProgressBar.Size = new System.Drawing.Size(460, 40);
			this.InstallationProgressBar.TabIndex = 0;
			// 
			// PhaseText
			// 
			this.PhaseText.Dock = System.Windows.Forms.DockStyle.Bottom;
			this.PhaseText.Location = new System.Drawing.Point(0, 0);
			this.PhaseText.Name = "PhaseText";
			this.PhaseText.Size = new System.Drawing.Size(460, 30);
			this.PhaseText.TabIndex = 1;
			this.PhaseText.Text = "Starting installation";
			this.PhaseText.TextAlign = System.Drawing.ContentAlignment.MiddleCenter;
			// 
			// PhaseTextPanel
			// 
			this.PhaseTextPanel.Controls.Add(this.PhaseText);
			this.PhaseTextPanel.Location = new System.Drawing.Point(12, 89);
			this.PhaseTextPanel.Name = "PhaseTextPanel";
			this.PhaseTextPanel.Size = new System.Drawing.Size(460, 30);
			this.PhaseTextPanel.TabIndex = 2;
			// 
			// InstallationBackgroundWorker
			// 
			this.InstallationBackgroundWorker.WorkerReportsProgress = true;
			this.InstallationBackgroundWorker.DoWork += new System.ComponentModel.DoWorkEventHandler(this.InstallationBackgroundWorker_DoWork);
			this.InstallationBackgroundWorker.ProgressChanged += new System.ComponentModel.ProgressChangedEventHandler(this.InstallationBackgroundWorker_ProgressChanged);
			this.InstallationBackgroundWorker.RunWorkerCompleted += new System.ComponentModel.RunWorkerCompletedEventHandler(this.InstallationBackgroundWorker_RunWorkerCompleted);
			// 
			// ProgressBar
			// 
			this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
			this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
			this.ClientSize = new System.Drawing.Size(484, 131);
			this.ControlBox = false;
			this.Controls.Add(this.PhaseTextPanel);
			this.Controls.Add(this.InstallationProgressBar);
			this.FormBorderStyle = System.Windows.Forms.FormBorderStyle.FixedSingle;
			this.MaximizeBox = false;
			this.MaximumSize = new System.Drawing.Size(500, 170);
			this.MinimizeBox = false;
			this.MinimumSize = new System.Drawing.Size(500, 170);
			this.Name = "ProgressBar";
			this.ShowIcon = false;
			this.StartPosition = System.Windows.Forms.FormStartPosition.CenterScreen;
			this.Text = "Installing Mod...";
			this.PhaseTextPanel.ResumeLayout(false);
			this.ResumeLayout(false);

		}

		#endregion

		private System.Windows.Forms.ProgressBar InstallationProgressBar;
		private System.Windows.Forms.Label PhaseText;
		private System.Windows.Forms.Panel PhaseTextPanel;
		private System.ComponentModel.BackgroundWorker InstallationBackgroundWorker;
	}
}