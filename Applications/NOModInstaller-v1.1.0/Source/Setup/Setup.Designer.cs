namespace NOModInstaller {
	partial class Setup {
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
			System.ComponentModel.ComponentResourceManager resources = new System.ComponentModel.ComponentResourceManager(typeof(Setup));
			this.InstallButton = new System.Windows.Forms.Button();
			this.InformationText = new System.Windows.Forms.Label();
			this.AdvancedButton = new System.Windows.Forms.Button();
			this.AbortButton = new System.Windows.Forms.Button();
			this.SuspendLayout();
			// 
			// InstallButton
			// 
			resources.ApplyResources(this.InstallButton, "InstallButton");
			this.InstallButton.Name = "InstallButton";
			this.InstallButton.UseVisualStyleBackColor = true;
			this.InstallButton.Click += new System.EventHandler(this.InstallButton_Click);
			// 
			// InformationText
			// 
			resources.ApplyResources(this.InformationText, "InformationText");
			this.InformationText.Name = "InformationText";
			// 
			// AdvancedButton
			// 
			resources.ApplyResources(this.AdvancedButton, "AdvancedButton");
			this.AdvancedButton.Name = "AdvancedButton";
			this.AdvancedButton.UseVisualStyleBackColor = true;
			this.AdvancedButton.Click += new System.EventHandler(this.AdvancedButton_Click);
			// 
			// AbortButton
			// 
			resources.ApplyResources(this.AbortButton, "AbortButton");
			this.AbortButton.Name = "AbortButton";
			this.AbortButton.UseVisualStyleBackColor = true;
			this.AbortButton.Click += new System.EventHandler(this.AbortButton_Click);
			// 
			// Setup
			// 
			resources.ApplyResources(this, "$this");
			this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
			this.Controls.Add(this.AbortButton);
			this.Controls.Add(this.AdvancedButton);
			this.Controls.Add(this.InformationText);
			this.Controls.Add(this.InstallButton);
			this.FormBorderStyle = System.Windows.Forms.FormBorderStyle.FixedSingle;
			this.MaximizeBox = false;
			this.MinimizeBox = false;
			this.Name = "Setup";
			this.ShowIcon = false;
			this.Load += new System.EventHandler(this.Setup_Load);
			this.ResumeLayout(false);
			this.PerformLayout();

		}

		#endregion

		private System.Windows.Forms.Button InstallButton;
		private System.Windows.Forms.Label InformationText;
		private System.Windows.Forms.Button AdvancedButton;
		private System.Windows.Forms.Button AbortButton;
	}
}

