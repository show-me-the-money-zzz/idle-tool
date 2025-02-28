namespace IdleTool.Util.Capture
{
    //using System;
    using System.Drawing;
    using System.Drawing.Imaging;
    using System.Windows.Forms;

    public partial class PreviewForm : Form
    {
        PictureBox _picbox;

        Button _btn_Save;
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

            // 저장 버튼 설정
            _btn_Save = new Button
            {
                Text = "저장",
                Dock = DockStyle.Bottom,
                Height = 40
            };
            _btn_Save.Click += (s, e) => {
                _picbox.Image.Save("captured.png", ImageFormat.Png);

                this.Close();
                MessageBox.Show("저장 완료!", "알림", MessageBoxButtons.OK, MessageBoxIcon.Information);
            };

            // 취소 버튼 설정
            _btn_Cancel = new Button {
                Text = "취소",
                Dock = DockStyle.Bottom,
                Height = 40
            };
            _btn_Cancel.Click += (s, e) => this.Close();

            {//컨트롤 추가
                this.Controls.Add(_picbox);

                this.Controls.Add(_btn_Save);
                this.Controls.Add(_btn_Cancel);
            }
        }
    }
}
