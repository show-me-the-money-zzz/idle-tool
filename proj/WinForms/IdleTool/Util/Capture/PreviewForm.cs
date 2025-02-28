namespace IdleTool.Util.Capture
{
    //using System;
    using System.Drawing;
    using System.Drawing.Imaging;
    using System.Windows.Forms;

    public partial class PreviewForm : Form
    {
        Common.Types.RECT _apprect = new Common.Types.RECT();
        Rectangle _rectangle = new Rectangle();

        public PreviewForm(Bitmap capturedImage, Rectangle __rectangle, Common.Types.RECT __apprect)
        {
            InitializeComponent(capturedImage);

            _apprect = __apprect;
            _rectangle = __rectangle;
            UpdateTextBox_Rect();
        }

        void UpdateTextBox_Rect()
        {
            _tbox_list_rect[0].Text = (_rectangle.X - _apprect.Left).ToString();
            _tbox_list_rect[1].Text = (_rectangle.Y - _apprect.Top).ToString();
            _tbox_list_rect[2].Text = (_rectangle.Right - _apprect.Left).ToString();
            _tbox_list_rect[3].Text = (_rectangle.Bottom - _apprect.Top).ToString();
        }

        #region [Event Handler]
        void OnClick_Save(object sender, EventArgs e)
        {
            _picbox.Image.Save($@".\captured ({_rectangle.X}, {_rectangle.Y}) ({_rectangle.Width} x {_rectangle.Height}).png", ImageFormat.Png);

            this.Close();
            MessageBox.Show("저장 완료!", "알림", MessageBoxButtons.OK, MessageBoxIcon.Information);
        }

        void OnClick_Retry(object sender, EventArgs e)
        {
            this.DialogResult = DialogResult.Retry;
            this.Close();
        }

        void Processs_KeyDown(object sender, KeyEventArgs e)
        {
            if (Keys.Escape == e.KeyData)
            {
                this.Close();
            }
        }
        #endregion
    }
}
