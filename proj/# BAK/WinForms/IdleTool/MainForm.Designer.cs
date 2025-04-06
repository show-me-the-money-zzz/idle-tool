using IdleTool.Controller;

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
            System.ComponentModel.ComponentResourceManager resources = new System.ComponentModel.ComponentResourceManager(typeof(MainForm));
            test_button1 = new Button();
            TXT_Logger = new TextBox();
            test_button2 = new Button();
            test_button3 = new Button();
            test_button4 = new Button();
            statusStrip = new StatusStrip();
            statusLabel_HP = new ToolStripStatusLabel();
            statusLabel_MP = new ToolStripStatusLabel();
            statusLabel_Potion = new ToolStripStatusLabel();
            statusLabel_State = new ToolStripStatusLabel();
            statusStrip.SuspendLayout();
            SuspendLayout();
            // 
            // test_button1
            // 
            test_button1.Location = new Point(123, 285);
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
            TXT_Logger.Size = new Size(560, 124);
            TXT_Logger.TabIndex = 1;
            // 
            // test_button2
            // 
            test_button2.Location = new Point(12, 285);
            test_button2.Name = "test_button2";
            test_button2.Size = new Size(105, 23);
            test_button2.TabIndex = 2;
            test_button2.Text = "인벤토리 찾기";
            test_button2.UseVisualStyleBackColor = true;
            test_button2.Click += OnClick_Test2;
            // 
            // test_button3
            // 
            test_button3.Location = new Point(12, 12);
            test_button3.Name = "test_button3";
            test_button3.Size = new Size(105, 23);
            test_button3.TabIndex = 3;
            test_button3.Text = "캡쳐하기";
            test_button3.UseVisualStyleBackColor = true;
            test_button3.Click += OnClick_Test3;
            // 
            // test_button4
            // 
            test_button4.Location = new Point(123, 12);
            test_button4.Name = "test_button4";
            test_button4.Size = new Size(105, 23);
            test_button4.TabIndex = 4;
            test_button4.Text = "키 테스트";
            test_button4.UseVisualStyleBackColor = true;
            test_button4.Click += OnClick_Test4;
            // 
            // statusStrip
            // 
            statusStrip.Items.AddRange(new ToolStripItem[] { statusLabel_HP, statusLabel_MP, statusLabel_Potion, statusLabel_State });
            statusStrip.Location = new Point(0, 439);
            statusStrip.Name = "statusStrip";
            statusStrip.Size = new Size(584, 22);
            statusStrip.TabIndex = 5;
            statusStrip.Text = "statusStrip1";
            // 
            // statusLabel_HP
            // 
            statusLabel_HP.AutoSize = false;
            statusLabel_HP.BorderSides = ToolStripStatusLabelBorderSides.Right;
            statusLabel_HP.ForeColor = SystemColors.ControlText;
            statusLabel_HP.ImageAlign = ContentAlignment.MiddleLeft;
            statusLabel_HP.Name = "statusLabel_HP";
            statusLabel_HP.Size = new Size(120, 17);
            // 
            // statusLabel_MP
            // 
            statusLabel_MP.AutoSize = false;
            statusLabel_MP.BorderSides = ToolStripStatusLabelBorderSides.Right;
            statusLabel_MP.ImageAlign = ContentAlignment.MiddleLeft;
            statusLabel_MP.Name = "statusLabel_MP";
            statusLabel_MP.Size = new Size(120, 17);
            // 
            // statusLabel_Potion
            // 
            statusLabel_Potion.AutoSize = false;
            statusLabel_Potion.BorderSides = ToolStripStatusLabelBorderSides.Right;
            statusLabel_Potion.ImageAlign = ContentAlignment.MiddleLeft;
            statusLabel_Potion.Name = "statusLabel_Potion";
            statusLabel_Potion.Size = new Size(120, 17);
            // 
            // statusLabel_State
            // 
            statusLabel_State.AutoSize = false;
            statusLabel_State.Name = "statusLabel_State";
            statusLabel_State.Size = new Size(209, 17);
            statusLabel_State.Spring = true;
            statusLabel_State.Text = "상태";
            statusLabel_State.TextAlign = ContentAlignment.MiddleRight;
            // 
            // MainForm
            // 
            AutoScaleDimensions = new SizeF(7F, 15F);
            AutoScaleMode = AutoScaleMode.Font;
            ClientSize = new Size(584, 461);
            Controls.Add(statusStrip);
            Controls.Add(test_button4);
            Controls.Add(test_button3);
            Controls.Add(test_button2);
            Controls.Add(TXT_Logger);
            Controls.Add(test_button1);
            FormBorderStyle = FormBorderStyle.FixedSingle;
            Icon = (Icon)resources.GetObject("$this.Icon");
            MaximizeBox = false;
            Name = "MainForm";
            Text = "쇼미더머니";
            KeyDown += Processs_KeyDown;
            statusStrip.ResumeLayout(false);
            statusStrip.PerformLayout();
            ResumeLayout(false);
            PerformLayout();
        }

        #endregion

        private Button test_button1;
        private TextBox TXT_Logger;
        private Button test_button2;
        private Button test_button3;
        private Button test_button4;
        private StatusStrip statusStrip;
        private ToolStripStatusLabel statusLabel_State;
        private ToolStripStatusLabel statusLabel_HP;
        private ToolStripStatusLabel statusLabel_MP;
        private ToolStripStatusLabel statusLabel_Potion;
    }
}
