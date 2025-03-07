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
            this.SuspendLayout();
            // 
            // TBOX_PID
            // 
            this.TBOX_PID.Location = new System.Drawing.Point(12, 12);
            this.TBOX_PID.Name = "TBOX_PID";
            this.TBOX_PID.Size = new System.Drawing.Size(143, 21);
            this.TBOX_PID.TabIndex = 0;
            // 
            // TBOX_PName
            // 
            this.TBOX_PName.Enabled = false;
            this.TBOX_PName.Location = new System.Drawing.Point(12, 105);
            this.TBOX_PName.Name = "TBOX_PName";
            this.TBOX_PName.Size = new System.Drawing.Size(143, 21);
            this.TBOX_PName.TabIndex = 1;
            // 
            // BTN_OK
            // 
            this.BTN_OK.Location = new System.Drawing.Point(177, 12);
            this.BTN_OK.Name = "BTN_OK";
            this.BTN_OK.Size = new System.Drawing.Size(75, 23);
            this.BTN_OK.TabIndex = 2;
            this.BTN_OK.Text = "PID 확인";
            this.BTN_OK.UseVisualStyleBackColor = true;
            this.BTN_OK.Click += OnClick_OK;
            // 
            // BTN_PROCOK
            // 
            this.BTN_PROCOK.Location = new System.Drawing.Point(177, 41);
            this.BTN_PROCOK.Name = "BTN_PROCOK";
            this.BTN_PROCOK.Size = new System.Drawing.Size(75, 23);
            this.BTN_PROCOK.TabIndex = 4;
            this.BTN_PROCOK.Text = "PROC 확인";
            this.BTN_PROCOK.UseVisualStyleBackColor = true;
            this.BTN_PROCOK.Click += OnClick_PorcOK;
            // 
            // BTN_COPY
            // 
            this.BTN_COPY.Location = new System.Drawing.Point(177, 103);
            this.BTN_COPY.Name = "BTN_COPY";
            this.BTN_COPY.Size = new System.Drawing.Size(75, 23);
            this.BTN_COPY.TabIndex = 3;
            this.BTN_COPY.Text = "복사";
            this.BTN_COPY.UseVisualStyleBackColor = true;
            this.BTN_COPY.Click += OnClick_Copy;
            // 
            // Form1
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(7F, 12F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(264, 138);
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
    }
}

