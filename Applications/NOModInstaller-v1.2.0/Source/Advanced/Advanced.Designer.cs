namespace NOModInstaller {
	partial class Advanced {
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
			System.ComponentModel.ComponentResourceManager resources = new System.ComponentModel.ComponentResourceManager(typeof(Advanced));
			this.UserDirectoryTextbox = new System.Windows.Forms.TextBox();
			this.InstallButton = new System.Windows.Forms.Button();
			this.AbortButton = new System.Windows.Forms.Button();
			this.UserDirectoryLabel = new System.Windows.Forms.Label();
			this.UserDirectoryTextboxButton = new System.Windows.Forms.Button();
			this.FolderBrowser = new System.Windows.Forms.FolderBrowserDialog();
			this.label1 = new System.Windows.Forms.Label();
			this.ModsDirectoryTextbox = new System.Windows.Forms.TextBox();
			this.SuspendLayout();
			// 
			// UserDirectoryTextbox
			// 
			resources.ApplyResources(this.UserDirectoryTextbox, "UserDirectoryTextbox");
			this.UserDirectoryTextbox.Name = "UserDirectoryTextbox";
			this.UserDirectoryTextbox.TextChanged += new System.EventHandler(this.UserDirectoryTextbox_TextChanged);
			// 
			// InstallButton
			// 
			resources.ApplyResources(this.InstallButton, "InstallButton");
			this.InstallButton.Name = "InstallButton";
			this.InstallButton.UseVisualStyleBackColor = true;
			this.InstallButton.Click += new System.EventHandler(this.InstallButton_Click);
			// 
			// AbortButton
			// 
			resources.ApplyResources(this.AbortButton, "AbortButton");
			this.AbortButton.Name = "AbortButton";
			this.AbortButton.UseVisualStyleBackColor = true;
			this.AbortButton.Click += new System.EventHandler(this.AbortButton_Click);
			// 
			// UserDirectoryLabel
			// 
			resources.ApplyResources(this.UserDirectoryLabel, "UserDirectoryLabel");
			this.UserDirectoryLabel.Name = "UserDirectoryLabel";
			// 
			// UserDirectoryTextboxButton
			// 
			resources.ApplyResources(this.UserDirectoryTextboxButton, "UserDirectoryTextboxButton");
			this.UserDirectoryTextboxButton.Name = "UserDirectoryTextboxButton";
			this.UserDirectoryTextboxButton.UseVisualStyleBackColor = true;
			this.UserDirectoryTextboxButton.Click += new System.EventHandler(this.UserDirectoryTextboxButton_Click);
			// 
			// FolderBrowser
			// 
			resources.ApplyResources(this.FolderBrowser, "FolderBrowser");
			this.FolderBrowser.RootFolder = System.Environment.SpecialFolder.MyComputer;
			// 
			// label1
			// 
			resources.ApplyResources(this.label1, "label1");
			this.label1.Name = "label1";
			// 
			// ModsDirectoryTextbox
			// 
			resources.ApplyResources(this.ModsDirectoryTextbox, "ModsDirectoryTextbox");
			this.ModsDirectoryTextbox.Name = "ModsDirectoryTextbox";
			this.ModsDirectoryTextbox.ReadOnly = true;
			// 
			// Advanced
			// 
			resources.ApplyResources(this, "$this");
			this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
			this.Controls.Add(this.ModsDirectoryTextbox);
			this.Controls.Add(this.label1);
			this.Controls.Add(this.UserDirectoryTextboxButton);
			this.Controls.Add(this.UserDirectoryLabel);
			this.Controls.Add(this.AbortButton);
			this.Controls.Add(this.InstallButton);
			this.Controls.Add(this.UserDirectoryTextbox);
			this.FormBorderStyle = System.Windows.Forms.FormBorderStyle.FixedSingle;
			this.MaximizeBox = false;
			this.MinimizeBox = false;
			this.Name = "Advanced";
			this.ShowIcon = false;
			this.Load += new System.EventHandler(this.Advanced_Load);
			this.ResumeLayout(false);
			this.PerformLayout();

		}

		#endregion

		private System.Windows.Forms.TextBox UserDirectoryTextbox;
		private System.Windows.Forms.Button InstallButton;
		private System.Windows.Forms.Button AbortButton;
		private System.Windows.Forms.Label UserDirectoryLabel;
		private System.Windows.Forms.Button UserDirectoryTextboxButton;
		private System.Windows.Forms.FolderBrowserDialog FolderBrowser;
		private System.Windows.Forms.Label label1;
		private System.Windows.Forms.TextBox ModsDirectoryTextbox;
	}
}