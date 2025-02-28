namespace IdleTool.Util.Capture
{
    using System.Drawing;
    using System.Drawing.Imaging;
    using System.Runtime.InteropServices;

    //using Emgu.CV.Reg;
    //using static Emgu.CV.OCR.Tesseract;

    public static class Tool
    {
        [DllImport("gdi32.dll")] static extern bool BitBlt(IntPtr hdcDest
            , int xDest, int yDest, int wDest, int hDest,
            IntPtr hdcSrc, int xSrc, int ySrc, int rop);

        private const int SRCCOPY = 0x00CC0020;

        public static Bitmap NewMake(Controller.App __app)
        {
            var rect = __app.Capture_Rect();

            //using (Bitmap bitmap = new Bitmap(__rect.Width, __rect.Height))
            //Bitmap bitmap = new Bitmap(rect.Width, rect.Height, PixelFormat.Format32bppArgb);
            //{
            //    using (Graphics g = Graphics.FromImage(bitmap))
            //    {
            //        g.CopyFromScreen(rect.Left, rect.Top, 0, 0, new Size(rect.Width, rect.Height), CopyPixelOperation.SourceCopy);
            //    }
            //}
            //return bitmap;

            return Make_Screen(rect.Get_Rectangle());
        }

        static Bitmap Make_Screen(Rectangle __rect)
        {
            Bitmap bitmap = new Bitmap(__rect.Width, __rect.Height
                , PixelFormat.Format32bppArgb//??
                );

            using (Graphics g = Graphics.FromImage(bitmap))
            {
                g.CopyFromScreen(__rect.Location, Point.Empty, __rect.Size
                    , CopyPixelOperation.SourceCopy//??
                    );
            }
            return bitmap;
        }

        public static void Make_Custom(Common.Types.RECT __apprect)
        {
            using (var form = new ScreenForm())
            {
                if(DialogResult.OK == form.ShowDialog())
                {
                    var rectangle = form.Get_SelectedRectangle();
                    if (0 < rectangle.Width && 0 < rectangle.Height)
                    {
                        var captured = Make_Screen(rectangle);
                        const int Preparation = 50;

                        if (__apprect.Left - Preparation <= rectangle.Left &&
                            __apprect.Top - Preparation <= rectangle.Top &&
                            __apprect.Right + Preparation >= rectangle.Right &&
                            __apprect.Bottom + Preparation >= rectangle.Bottom
                            )
                        {
                            // 새로운 창으로 이미지 표시 (저장하지 않음)
                            var preview = new PreviewForm(captured, rectangle, __apprect);
                            if (DialogResult.Retry == preview.ShowDialog())
                            {
                                Make_Custom(__apprect);
                            }
                        }
                        else
                        {
                            MessageBox.Show("게임 내의 영역을 캡쳐해 주세요", "에러", MessageBoxButtons.OK, MessageBoxIcon.Information);
                        }
                    }
                }
            }
        }

        public static Bitmap Make_Cropped(Controller.App __app, Rectangle region)
        {//앱의 특정 위치를 캡쳐
            var rect_app = __app.Capture_Rect();

            Bitmap bitmap = new Bitmap(region.Width, region.Height, PixelFormat.Format32bppArgb);
            {
                using (Graphics g = Graphics.FromImage(bitmap))
                {
                    g.CopyFromScreen(rect_app.Left + region.Left, rect_app.Top + region.Top
                        , 0, 0
                        , new Size(region.Width, region.Height)
                        , CopyPixelOperation.SourceCopy);
                }
            }
            return bitmap;
        }

        //[DllImport("user32.dll")]
        //static extern bool PrintWindow(IntPtr hwnd, IntPtr hdcBlt, uint nFlags);
        public static Bitmap NewMake_DC(Controller.App __app)
        {//ChatGPT
            // 창의 DC 가져오기
            IntPtr hDC = Util.Importer.Get_DC(__app.HANDLE);
            var rect = __app.Capture_Rect();

            // 비트맵 생성 및 DC 가져오기
            Bitmap bmp = new Bitmap(rect.Width, rect.Height, PixelFormat.Format32bppArgb);
            using (Graphics gfx = Graphics.FromImage(bmp))
            {
                IntPtr hdcBitmap = gfx.GetHdc();

                BitBlt(hdcBitmap, 0, 0, rect.Width, rect.Height, hDC
                    , 0, 0
                    //, rect.Left, rect.Top

                    , SRCCOPY);
                //PrintWindow(__app.HANDLE, hdcBitmap, 0);

                gfx.ReleaseHdc(hdcBitmap);
            }

            // DC 해제
            Util.Importer.Release_DC(__app.HANDLE, hDC);

            return bmp;
        }
    }
}
