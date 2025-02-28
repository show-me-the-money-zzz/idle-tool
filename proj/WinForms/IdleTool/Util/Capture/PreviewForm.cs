namespace IdleTool.Util.Capture
{
    //using System;
    using System.Drawing;
    using System.Drawing.Imaging;
    using System.Windows.Forms;

    public partial class PreviewForm : Form
    {
        public PreviewForm(Bitmap capturedImage)
        {
            InitializeComponent();
            _picbox.Image = capturedImage;
        }

        #region [Event Handler]
        void OnClick_Save(object sender, EventArgs e)
        {
            _picbox.Image.Save("captured.png", ImageFormat.Png);

            this.Close();
            MessageBox.Show("저장 완료!", "알림", MessageBoxButtons.OK, MessageBoxIcon.Information);
        }

        void OnClick_Cancel(object sender, EventArgs e) => this.Close();
        #endregion
    }
}
