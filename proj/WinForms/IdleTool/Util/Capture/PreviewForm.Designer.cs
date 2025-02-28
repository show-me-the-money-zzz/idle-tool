namespace IdleTool.Util.Capture
{
    using System.Windows.Forms;

    partial class PreviewForm
    {
        System.ComponentModel.IContainer components = null;

        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        void InitializeComponent()
        {
            var resources = new System.ComponentModel.ComponentResourceManager(typeof(PreviewForm));

            // PictureBox 설정
            _picbox = new PictureBox {
                //Image = capturedImage,
                SizeMode = PictureBoxSizeMode.AutoSize,
                Dock = DockStyle.Fill
            };

            // 저장 버튼 설정
            _btn_Save = new Button {
                Text = "저장",
                Dock = DockStyle.Bottom,
                Height = 40
            };
            _btn_Save.Click += OnClick_Save;

            // 취소 버튼 설정
            _btn_Cancel = new Button {
                Text = "취소",
                Dock = DockStyle.Bottom,
                Height = 40
            };
            _btn_Cancel.Click += OnClick_Cancel;

            {
                Controls.Add(_picbox);

                Controls.Add(_btn_Save);
                Controls.Add(_btn_Cancel);
            }

            {// 폼 기본 설정
                this.Text = "미리보기";
                this.StartPosition = FormStartPosition.CenterScreen;
                this.FormBorderStyle = FormBorderStyle.FixedDialog;
                this.MaximizeBox = false;
                this.MinimizeBox = false;
                this.AutoSize = true;
                this.AutoSizeMode = AutoSizeMode.GrowAndShrink;
            }
        }

        #region [Controls]
        PictureBox _picbox;

        Button _btn_Save;
        Button _btn_Cancel;
        #endregion
    }
}
