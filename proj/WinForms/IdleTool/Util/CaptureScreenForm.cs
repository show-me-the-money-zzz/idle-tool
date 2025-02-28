namespace IdleTool.Util
{
    using System;
    using System.Drawing;
    //using System.Drawing.Imaging;
    using System.Windows.Forms;

    internal class CaptureScreenForm : Form
    {
        Point _point_start;
        Rectangle _rect_selection;
        bool _isSelecting = false;

        public CaptureScreenForm()
        {
            this.DoubleBuffered = true;
            this.FormBorderStyle = FormBorderStyle.None;
            this.BackColor = Color.Black;
            this.Opacity = 0.5; // 반투명 효과
            this.TopMost = true;
            this.Cursor = Cursors.Cross;
            this.KeyPreview = true; // 키 입력을 받을 수 있도록 설정

            //this.WindowState = FormWindowState.Maximized;//주 모니터에서만 실행되는 문제 발생
            {// 모든 모니터의 해상도를 합쳐서 전체 화면 설정
                Rectangle totalBounds = Get_TotalScreenBounds();
                this.Bounds = totalBounds;
            }
        }

        // 여러 모니터 해상도를 합산하여 전체 크기 반환
        Rectangle Get_TotalScreenBounds()
        {
            int minX = Screen.AllScreens.Min(s => s.Bounds.Left);
            int minY = Screen.AllScreens.Min(s => s.Bounds.Top);
            int maxX = Screen.AllScreens.Max(s => s.Bounds.Right);
            int maxY = Screen.AllScreens.Max(s => s.Bounds.Bottom);

            return new Rectangle(minX, minY, maxX - minX, maxY - minY);
        }

        protected override void OnMouseDown(MouseEventArgs e)
        {
            if (e.Button == MouseButtons.Left)
            {
                _isSelecting = true;
                _point_start = e.Location;
                _rect_selection = new Rectangle(e.Location, new Size(0, 0));
            }
            else if (e.Button == MouseButtons.Right)
            {
                this.DialogResult = DialogResult.Cancel; // 마우스 우클릭으로 취소
                this.Close();
            }
        }

        protected override void OnMouseMove(MouseEventArgs e)
        {
            if (_isSelecting)
            {
                int x = Math.Min(_point_start.X, e.X);
                int y = Math.Min(_point_start.Y, e.Y);
                int width = Math.Abs(e.X - _point_start.X);
                int height = Math.Abs(e.Y - _point_start.Y);

                _rect_selection = new Rectangle(x, y, width, height);

                this.Invalidate(); // 화면 갱신
            }
        }

        // ESC 키로 캡처 취소 기능 추가
        protected override void OnKeyDown(KeyEventArgs e)
        {
            if (e.KeyCode == Keys.Escape)
            {
                this.DialogResult = DialogResult.Cancel;
                this.Close();
            }
            base.OnKeyDown(e);
        }

        protected override void OnMouseUp(MouseEventArgs e)
        {
            if (_isSelecting)
            {
                _isSelecting = false;

                this.DialogResult = DialogResult.OK;
                this.Close();
            }
        }

        protected override void OnPaint(PaintEventArgs e)
        {
            if (_isSelecting)
            {
                using (Pen pen = new Pen(Color.Red, 2))
                {
                    e.Graphics.DrawRectangle(pen, _rect_selection);
                }
            }
        }

        public Rectangle Get_SelectedRectangle()
        {
            return _rect_selection;
        }
    }
}
