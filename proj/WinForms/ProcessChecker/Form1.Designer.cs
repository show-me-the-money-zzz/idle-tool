namespace ProcessChecker
{
    partial class Form1
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
            System.ComponentModel.ComponentResourceManager resources = new System.ComponentModel.ComponentResourceManager(typeof(Form1));
            panel1 = new Panel();
            BTN_CHECK_PNAME = new Button();
            TBOX_PNAME = new TextBox();
            LBL_PNAME = new Label();
            BTN_CHECK_PID = new Button();
            TBOX_PID = new TextBox();
            LBL_PID = new Label();
            panel2 = new Panel();
            TBOX_HANDLE = new TextBox();
            LBL_HANDLE = new Label();
            BTN_COPY = new Button();
            TBOX_RESULT = new TextBox();
            LBL_RESULT = new Label();
            panel1.SuspendLayout();
            panel2.SuspendLayout();
            SuspendLayout();
            // 
            // panel1
            // 
            panel1.BorderStyle = BorderStyle.FixedSingle;
            panel1.Controls.Add(BTN_CHECK_PNAME);
            panel1.Controls.Add(TBOX_PNAME);
            panel1.Controls.Add(LBL_PNAME);
            panel1.Controls.Add(BTN_CHECK_PID);
            panel1.Controls.Add(TBOX_PID);
            panel1.Controls.Add(LBL_PID);
            panel1.Location = new Point(12, 12);
            panel1.Name = "panel1";
            panel1.Size = new Size(370, 80);
            panel1.TabIndex = 0;
            // 
            // BTN_CHECK_PNAME
            // 
            BTN_CHECK_PNAME.Location = new Point(272, 48);
            BTN_CHECK_PNAME.Name = "BTN_CHECK_PNAME";
            BTN_CHECK_PNAME.Size = new Size(75, 23);
            BTN_CHECK_PNAME.TabIndex = 5;
            BTN_CHECK_PNAME.Text = "확인";
            BTN_CHECK_PNAME.UseVisualStyleBackColor = true;
            BTN_CHECK_PNAME.Click += OnClick_Check_PName;
            // 
            // TBOX_PNAME
            // 
            TBOX_PNAME.Location = new Point(105, 45);
            TBOX_PNAME.Name = "TBOX_PNAME";
            TBOX_PNAME.Size = new Size(150, 23);
            TBOX_PNAME.TabIndex = 4;
            // 
            // LBL_PNAME
            // 
            LBL_PNAME.AutoSize = true;
            LBL_PNAME.Font = new Font("맑은 고딕", 9F, FontStyle.Bold);
            LBL_PNAME.Location = new Point(16, 48);
            LBL_PNAME.Name = "LBL_PNAME";
            LBL_PNAME.Size = new Size(83, 15);
            LBL_PNAME.TabIndex = 3;
            LBL_PNAME.Text = "프로세스 이름";
            // 
            // BTN_CHECK_PID
            // 
            BTN_CHECK_PID.Location = new Point(272, 10);
            BTN_CHECK_PID.Name = "BTN_CHECK_PID";
            BTN_CHECK_PID.Size = new Size(75, 23);
            BTN_CHECK_PID.TabIndex = 2;
            BTN_CHECK_PID.Text = "확인";
            BTN_CHECK_PID.UseVisualStyleBackColor = true;
            BTN_CHECK_PID.Click += OnClick_Check_PID;
            // 
            // TBOX_PID
            // 
            TBOX_PID.Location = new Point(105, 7);
            TBOX_PID.Name = "TBOX_PID";
            TBOX_PID.Size = new Size(150, 23);
            TBOX_PID.TabIndex = 1;
            // 
            // LBL_PID
            // 
            LBL_PID.AutoSize = true;
            LBL_PID.Font = new Font("맑은 고딕", 9F, FontStyle.Bold);
            LBL_PID.Location = new Point(16, 10);
            LBL_PID.Name = "LBL_PID";
            LBL_PID.Size = new Size(27, 15);
            LBL_PID.TabIndex = 0;
            LBL_PID.Text = "PID";
            // 
            // panel2
            // 
            panel2.BorderStyle = BorderStyle.FixedSingle;
            panel2.Controls.Add(TBOX_HANDLE);
            panel2.Controls.Add(LBL_HANDLE);
            panel2.Controls.Add(BTN_COPY);
            panel2.Controls.Add(TBOX_RESULT);
            panel2.Controls.Add(LBL_RESULT);
            panel2.Location = new Point(12, 114);
            panel2.Name = "panel2";
            panel2.Size = new Size(370, 80);
            panel2.TabIndex = 6;
            // 
            // TBOX_HANDLE
            // 
            TBOX_HANDLE.Enabled = false;
            TBOX_HANDLE.Location = new Point(105, 45);
            TBOX_HANDLE.Name = "TBOX_HANDLE";
            TBOX_HANDLE.Size = new Size(150, 23);
            TBOX_HANDLE.TabIndex = 4;
            // 
            // LBL_HANDLE
            // 
            LBL_HANDLE.AutoSize = true;
            LBL_HANDLE.Font = new Font("맑은 고딕", 9F, FontStyle.Bold);
            LBL_HANDLE.Location = new Point(16, 48);
            LBL_HANDLE.Name = "LBL_HANDLE";
            LBL_HANDLE.Size = new Size(55, 15);
            LBL_HANDLE.TabIndex = 3;
            LBL_HANDLE.Text = "HANDLE";
            // 
            // BTN_COPY
            // 
            BTN_COPY.Location = new Point(272, 10);
            BTN_COPY.Name = "BTN_COPY";
            BTN_COPY.Size = new Size(75, 23);
            BTN_COPY.TabIndex = 2;
            BTN_COPY.Text = "복사";
            BTN_COPY.UseVisualStyleBackColor = true;
            BTN_COPY.Click += OnClick_Copy;
            // 
            // TBOX_RESULT
            // 
            TBOX_RESULT.Enabled = false;
            TBOX_RESULT.Location = new Point(105, 7);
            TBOX_RESULT.Name = "TBOX_RESULT";
            TBOX_RESULT.Size = new Size(150, 23);
            TBOX_RESULT.TabIndex = 1;
            // 
            // LBL_RESULT
            // 
            LBL_RESULT.AutoSize = true;
            LBL_RESULT.Font = new Font("맑은 고딕", 9F, FontStyle.Bold);
            LBL_RESULT.Location = new Point(16, 10);
            LBL_RESULT.Name = "LBL_RESULT";
            LBL_RESULT.Size = new Size(31, 15);
            LBL_RESULT.TabIndex = 0;
            LBL_RESULT.Text = "결과";
            // 
            // Form1
            // 
            AutoScaleDimensions = new SizeF(7F, 15F);
            AutoScaleMode = AutoScaleMode.Font;
            ClientSize = new Size(404, 211);
            Controls.Add(panel2);
            Controls.Add(panel1);
            Icon = (Icon)resources.GetObject("$this.Icon");
            MaximizeBox = false;
            Name = "Form1";
            Text = "PID 체커";
            panel1.ResumeLayout(false);
            panel1.PerformLayout();
            panel2.ResumeLayout(false);
            panel2.PerformLayout();
            ResumeLayout(false);
        }

        #endregion

        private Panel panel1;
        private Button BTN_CHECK_PID;
        private TextBox TBOX_PID;
        private Label LBL_PID;
        private Button BTN_CHECK_PNAME;
        private TextBox TBOX_PNAME;
        private Label LBL_PNAME;
        private Panel panel2;
        private Button button1;
        private TextBox TBOX_HANDLE;
        private Label LBL_HANDLE;
        private Button BTN_COPY;
        private TextBox TBOX_RESULT;
        private Label LBL_RESULT;
    }
}
