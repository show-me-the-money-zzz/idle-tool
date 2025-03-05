namespace IdleTool.Util.Capture
{
    using System.Diagnostics;
    //using System;
    using System.Drawing;
    using System.Drawing.Imaging;
    using System.Windows.Forms;

    public partial class PreviewForm : Form
    {
        Common.Types.RECT _apprect = new Common.Types.RECT();
        Rectangle _rectangle = new Rectangle();
        
        Rectangle _this_rectangle = new Rectangle();
        public Rectangle UpdateRectangle => _this_rectangle;

        public PreviewForm(Bitmap capturedImage, Rectangle __rectangle, Common.Types.RECT __apprect)
        {
            InitializeComponent(capturedImage);

            _apprect = __apprect;
            _rectangle = __rectangle;
            _this_rectangle = __rectangle;
            UpdateTextBox_Rect();
        }

        void UpdateTextBox_Rect()
        {
            _tbox_list_rect[0].Text = (_this_rectangle.X - _apprect.Left).ToString();
            _tbox_list_rect[1].Text = (_this_rectangle.Y - _apprect.Top).ToString();

            //_tbox_list_rect[2].Text = (_this_rectangle.Width).ToString();
            //_tbox_list_rect[3].Text = (_this_rectangle.Height).ToString();
            _tbox_list_rect[2].Text = (_this_rectangle.Right - _apprect.Left).ToString();
            _tbox_list_rect[3].Text = (_this_rectangle.Bottom - _apprect.Top).ToString();
        }

        #region [Event Handler]
        void OnClick_Save(object sender, EventArgs e)
        {
            //Console.WriteLine($"OnClick_Save(): {_txtbox_Name.Text}");

            _picbox.Image.Save($@".\captured ({_rectangle.X}, {_rectangle.Y}) ({_rectangle.Width} x {_rectangle.Height}).png", ImageFormat.Png);

            this.Close();
            MessageBox.Show("저장 완료!", "알림", MessageBoxButtons.OK, MessageBoxIcon.Information);
        }

        void OnClick_Retry(object sender, EventArgs e)
        {
            this.DialogResult = DialogResult.Retry;
            this.Close();
        }

        void OnClick_Update_Rect(object sender, EventArgs e)
        {
            var L = int.Parse(_tbox_list_rect[0].Text);
            var T = int.Parse(_tbox_list_rect[1].Text);
            var R = int.Parse(_tbox_list_rect[2].Text);
            var B = int.Parse(_tbox_list_rect[3].Text);
            //Console.WriteLine($"Update_Rect: L= {L}, T= {T}, R= {R}, B= {B}");

            _this_rectangle.X = _apprect.Left + L;
            _this_rectangle.Y = _apprect.Top + T;
            _this_rectangle.Width = R - L;
            _this_rectangle.Height = B - T;
            //Console.WriteLine($"{_rectangle} vs {_this_rectangle}");

            this.DialogResult = DialogResult.TryAgain;
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
