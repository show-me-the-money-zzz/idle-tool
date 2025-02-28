namespace IdleTool.Util.Capture
{
    using System;
    using System.Drawing;
    using System.Windows.Forms;
    using static System.Windows.Forms.VisualStyles.VisualStyleElement.Window;

    internal class PreviewForm : Form
    {
        PictureBox _picbox;

        Button _btn_Cancel;

        public PreviewForm(Bitmap capturedImage)
        {
            // 폼 기본 설정
            this.Text = "미리보기";
            this.StartPosition = FormStartPosition.CenterScreen;
            this.FormBorderStyle = FormBorderStyle.FixedDialog;
            this.MaximizeBox = false;
            this.MinimizeBox = false;
            this.AutoSize = true;
            this.AutoSizeMode = AutoSizeMode.GrowAndShrink;

            Initialize_Controls();
            _picbox.Image = capturedImage;
        }

        void Initialize_Controls()
        {
            // PictureBox 설정
            _picbox = new PictureBox {
                //Image = capturedImage,
                SizeMode = PictureBoxSizeMode.AutoSize,
                Dock = DockStyle.Fill
            };

            // 닫기 버튼 설정
            _btn_Cancel = new Button {
                Text = "취소",
                Dock = DockStyle.Bottom,
                Height = 40
            };
            _btn_Cancel.Click += (s, e) => this.Close();

            //컨트롤 추가
            this.Controls.Add(_picbox);
            this.Controls.Add(_btn_Cancel);
        }
    }
}
