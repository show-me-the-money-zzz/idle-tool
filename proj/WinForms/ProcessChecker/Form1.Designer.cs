namespace ProcessChecker
{
    partial class Form1
    {
        /// <summary>
        /// 필수 디자이너 변수입니다.
        /// </summary>
        private System.ComponentModel.IContainer components = null;

        /// <summary>
        /// 사용 중인 모든 리소스를 정리합니다.
        /// </summary>
        /// <param name="disposing">관리되는 리소스를 삭제해야 하면 true이고, 그렇지 않으면 false입니다.</param>
        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Windows Form 디자이너에서 생성한 코드

        /// <summary>
        /// 디자이너 지원에 필요한 메서드입니다. 
        /// 이 메서드의 내용을 코드 편집기로 수정하지 마세요.
        /// </summary>
        private void InitializeComponent()
        {
            System.ComponentModel.ComponentResourceManager resources = new System.ComponentModel.ComponentResourceManager(typeof(Form1));
            this.TBOX_PID = new System.Windows.Forms.TextBox();
            this.TBOX_PName = new System.Windows.Forms.TextBox();
            this.BTN_OK = new System.Windows.Forms.Button();
            this.BTN_COPY = new System.Windows.Forms.Button();
            this.BTN_PROCOK = new System.Windows.Forms.Button();
            this.LBL_PID = new System.Windows.Forms.Label();
            this.LBL_PNAME = new System.Windows.Forms.Label();
            this.TBOX_Result = new System.Windows.Forms.TextBox();
            this.LBL_Result = new System.Windows.Forms.Label();
            this.LBL_Handle = new System.Windows.Forms.Label();
            this.TBOX_Handle = new System.Windows.Forms.TextBox();
            this.label1 = new System.Windows.Forms.Label();
            this.SuspendLayout();
            // 
            // TBOX_PID
            // 
            this.TBOX_PID.Location = new System.Drawing.Point(150, 12);
            this.TBOX_PID.Name = "TBOX_PID";
            this.TBOX_PID.Size = new System.Drawing.Size(143, 21);
            this.TBOX_PID.TabIndex = 0;
            // 
            // TBOX_PName
            // 
            this.TBOX_PName.Location = new System.Drawing.Point(150, 43);
            this.TBOX_PName.Name = "TBOX_PName";
            this.TBOX_PName.Size = new System.Drawing.Size(143, 21);
            this.TBOX_PName.TabIndex = 1;
            // 
            // BTN_OK
            // 
            this.BTN_OK.Location = new System.Drawing.Point(315, 12);
            this.BTN_OK.Name = "BTN_OK";
            this.BTN_OK.Size = new System.Drawing.Size(46, 23);
            this.BTN_OK.TabIndex = 2;
            this.BTN_OK.Text = "확인";
            this.BTN_OK.UseVisualStyleBackColor = true;
			this.BTN_OK.Click += OnClick_OK;
            // 
            // BTN_PROCOK
            // 
            this.BTN_PROCOK.Location = new System.Drawing.Point(315, 41);
            this.BTN_PROCOK.Name = "BTN_PROCOK";
            this.BTN_PROCOK.Size = new System.Drawing.Size(46, 23);
            this.BTN_PROCOK.TabIndex = 4;
            this.BTN_PROCOK.Text = "확인";
            this.BTN_PROCOK.UseVisualStyleBackColor = true;
            this.BTN_PROCOK.Click += OnClick_PorcOK;
            // 
            // BTN_COPY
            // 
            this.BTN_COPY.Location = new System.Drawing.Point(315, 103);
            this.BTN_COPY.Name = "BTN_COPY";
            this.BTN_COPY.Size = new System.Drawing.Size(46, 23);
            this.BTN_COPY.TabIndex = 3;
            this.BTN_COPY.Text = "복사";
            this.BTN_COPY.UseVisualStyleBackColor = true;
			this.BTN_COPY.Click += OnClick_Copy;
            // 
            // LBL_PID
            // 
            this.LBL_PID.Font = new System.Drawing.Font("굴림", 11F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(129)));
            this.LBL_PID.Location = new System.Drawing.Point(32, 14);
            this.LBL_PID.Name = "LBL_PID";
            this.LBL_PID.Size = new System.Drawing.Size(112, 21);
            this.LBL_PID.TabIndex = 5;
            this.LBL_PID.Text = "PID";
            // 
            // LBL_PNAME
            // 
            this.LBL_PNAME.Font = new System.Drawing.Font("굴림", 11F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(129)));
            this.LBL_PNAME.Location = new System.Drawing.Point(32, 41);
            this.LBL_PNAME.Name = "LBL_PNAME";
            this.LBL_PNAME.Size = new System.Drawing.Size(112, 21);
            this.LBL_PNAME.TabIndex = 6;
            this.LBL_PNAME.Text = "프로세스 이름";
            // 
            // TBOX_Result
            // 
            this.TBOX_Result.Enabled = false;
            this.TBOX_Result.Location = new System.Drawing.Point(150, 103);
            this.TBOX_Result.Name = "TBOX_Result";
            this.TBOX_Result.Size = new System.Drawing.Size(143, 21);
            this.TBOX_Result.TabIndex = 7;
            // 
            // LBL_Result
            // 
            this.LBL_Result.Font = new System.Drawing.Font("굴림", 11F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(129)));
            this.LBL_Result.Location = new System.Drawing.Point(32, 103);
            this.LBL_Result.Name = "LBL_Result";
            this.LBL_Result.Size = new System.Drawing.Size(112, 21);
            this.LBL_Result.TabIndex = 8;
            this.LBL_Result.Text = "결과";
            // 
            // LBL_Handle
            // 
            this.LBL_Handle.Font = new System.Drawing.Font("굴림", 11F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(129)));
            this.LBL_Handle.Location = new System.Drawing.Point(32, 137);
            this.LBL_Handle.Name = "LBL_Handle";
            this.LBL_Handle.Size = new System.Drawing.Size(112, 21);
            this.LBL_Handle.TabIndex = 9;
            this.LBL_Handle.Text = "HANDLE";
            // 
            // TBOX_Handle
            // 
            this.TBOX_Handle.Enabled = false;
            this.TBOX_Handle.Location = new System.Drawing.Point(150, 137);
            this.TBOX_Handle.Name = "TBOX_Handle";
            this.TBOX_Handle.Size = new System.Drawing.Size(143, 21);
            this.TBOX_Handle.TabIndex = 10;
            // 
            // label1
            // 
            this.label1.Location = new System.Drawing.Point(21, 77);
            this.label1.Name = "label1";
            this.label1.Size = new System.Drawing.Size(360, 12);
            this.label1.TabIndex = 11;
            this.label1.Text = "-----------------------------------------------------------";
            // 
            // Form1
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(7F, 12F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(404, 181);
            this.Controls.Add(this.label1);
            this.Controls.Add(this.TBOX_Handle);
            this.Controls.Add(this.LBL_Handle);
            this.Controls.Add(this.LBL_Result);
            this.Controls.Add(this.TBOX_Result);
            this.Controls.Add(this.LBL_PNAME);
            this.Controls.Add(this.LBL_PID);
            this.Controls.Add(this.BTN_PROCOK);
            this.Controls.Add(this.BTN_COPY);
            this.Controls.Add(this.BTN_OK);
            this.Controls.Add(this.TBOX_PName);
            this.Controls.Add(this.TBOX_PID);
            this.Icon = ((System.Drawing.Icon)(resources.GetObject("$this.Icon")));
            this.Name = "Form1";
            this.Text = "Process Checker";
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        #endregion

        private System.Windows.Forms.TextBox TBOX_PID;
        private System.Windows.Forms.TextBox TBOX_PName;

        private System.Windows.Forms.Button BTN_OK;
        private System.Windows.Forms.Button BTN_PROCOK;

        private System.Windows.Forms.Button BTN_COPY;
        private System.Windows.Forms.Label LBL_PID;
        private System.Windows.Forms.Label LBL_PNAME;
        private System.Windows.Forms.TextBox TBOX_Result;
        private System.Windows.Forms.Label LBL_Result;
        private System.Windows.Forms.Label LBL_Handle;
        private System.Windows.Forms.TextBox TBOX_Handle;
        private System.Windows.Forms.Label label1;
    }
}

