namespace NOModUninstaller {
	partial class Completion {
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
			System.ComponentModel.ComponentResourceManager resources = new System.ComponentModel.ComponentResourceManager(typeof(Completion));
			this.CompletionInformation = new System.Windows.Forms.Label();
			this.FinishButton = new System.Windows.Forms.Button();
			this.SuspendLayout();
			// 
			// CompletionInformation
			// 
			resources.ApplyResources(this.CompletionInformation, "CompletionInformation");
			this.CompletionInformation.Name = "CompletionInformation";
			// 
			// FinishButton
			// 
			resources.ApplyResources(this.FinishButton, "FinishButton");
			this.FinishButton.Name = "FinishButton";
			this.FinishButton.UseVisualStyleBackColor = true;
			this.FinishButton.Click += new System.EventHandler(this.FinishButton_Click);
			// 
			// Completion
			// 
			resources.ApplyResources(this, "$this");
			this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
			this.Controls.Add(this.FinishButton);
			this.Controls.Add(this.CompletionInformation);
			this.FormBorderStyle = System.Windows.Forms.FormBorderStyle.FixedSingle;
			this.MaximizeBox = false;
			this.MinimizeBox = false;
			this.Name = "Completion";
			this.ShowIcon = false;
			this.ResumeLayout(false);
			this.PerformLayout();

		}

		#endregion

		private System.Windows.Forms.Label CompletionInformation;
		private System.Windows.Forms.Button FinishButton;
	}
}