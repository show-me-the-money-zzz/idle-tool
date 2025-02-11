namespace IdleTool
{
    partial class MainForm
    {
        /// <summary>
        ///  Required designer variable.
        /// </summary>
        private System.ComponentModel.IContainer components = null;

        /// <summary>
        ///  Clean up any resources being used.
        /// </summary>
        /// <param name="disposing">true if managed resources should be disposed; otherwise, false.</param>
        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Windows Form Designer generated code

        /// <summary>
        ///  Required method for Designer support - do not modify
        ///  the contents of this method with the code editor.
        /// </summary>
        private void InitializeComponent()
        {
            test_button1 = new Button();
            TXT_Logger = new TextBox();
            test_button2 = new Button();
            test_button3 = new Button();
            SuspendLayout();
            // 
            // test_button1
            // 
            test_button1.Location = new Point(12, 12);
            test_button1.Name = "test_button1";
            test_button1.Size = new Size(105, 23);
            test_button1.TabIndex = 0;
            test_button1.Text = "지도 찾기";
            test_button1.UseVisualStyleBackColor = true;
            test_button1.Click += OnClick_Test1;
            // 
            // TXT_Logger
            // 
            TXT_Logger.Location = new Point(12, 314);
            TXT_Logger.Multiline = true;
            TXT_Logger.Name = "TXT_Logger";
            TXT_Logger.Size = new Size(776, 124);
            TXT_Logger.TabIndex = 1;
            // 
            // test_button2
            // 
            test_button2.Location = new Point(12, 41);
            test_button2.Name = "test_button2";
            test_button2.Size = new Size(105, 23);
            test_button2.TabIndex = 2;
            test_button2.Text = "인벤토리 찾기";
            test_button2.UseVisualStyleBackColor = true;
            test_button2.Click += OnClick_Test2;
            // 
            // test_button3
            // 
            test_button3.Location = new Point(12, 285);
            test_button3.Name = "test_button3";
            test_button3.Size = new Size(105, 23);
            test_button3.TabIndex = 3;
            test_button3.Text = "텍스트 찾기";
            test_button3.UseVisualStyleBackColor = true;
            test_button3.Click += OnClick_Test3;
            // 
            // MainForm
            // 
            AutoScaleDimensions = new SizeF(7F, 15F);
            AutoScaleMode = AutoScaleMode.Font;
            ClientSize = new Size(800, 450);
            Controls.Add(test_button3);
            Controls.Add(test_button2);
            Controls.Add(TXT_Logger);
            Controls.Add(test_button1);
            Name = "MainForm";
            Text = "쇼미더머니 - LORDNINE";
            KeyDown += Processs_KeyDown;
            ResumeLayout(false);
            PerformLayout();
        }

        #endregion

        private Button test_button1;
        private TextBox TXT_Logger;
        private Button test_button2;
        private Button test_button3;
    }
}
