namespace IdleTool.Util.Capture
{
    //using System;
    using System.Drawing;
    using System.Drawing.Imaging;
    using System.Windows.Forms;

    public partial class PreviewForm : Form
    {
        Rectangle _rectangle = new Rectangle();

        public PreviewForm(Bitmap capturedImage, Rectangle __rectangle)
        {
            InitializeComponent(capturedImage);

            _rectangle = __rectangle;
        }

        #region [Event Handler]
        void OnClick_Save(object sender, EventArgs e)
        {
            _picbox.Image.Save($@".\captured ({_rectangle.X}, {_rectangle.Y}) ({_rectangle.Width} x {_rectangle.Height}).png", ImageFormat.Png);

            this.Close();
            MessageBox.Show("저장 완료!", "알림", MessageBoxButtons.OK, MessageBoxIcon.Information);
        }

        void OnClick_Cancel(object sender, EventArgs e) => this.Close();
        #endregion
    }
}
