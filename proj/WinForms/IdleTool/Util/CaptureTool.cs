namespace IdleTool.Util
{
    using System.Drawing;
    using System.Drawing.Imaging;
    using System.Runtime.InteropServices;

    //using Emgu.CV.Reg;
    //using static Emgu.CV.OCR.Tesseract;

    public static class CaptureTool
    {
        [DllImport("gdi32.dll")] static extern bool BitBlt(IntPtr hdcDest
            , int xDest, int yDest, int wDest, int hDest,
            IntPtr hdcSrc, int xSrc, int ySrc, int rop);

        private const int SRCCOPY = 0x00CC0020;

        public static Bitmap NewMake(Controller.App __app)
        {
            var rect = __app.Capture_Rect();

            //using (Bitmap bitmap = new Bitmap(__rect.Width, __rect.Height))
            Bitmap bitmap = new Bitmap(rect.Width, rect.Height, PixelFormat.Format32bppArgb);
            {
                using (Graphics g = Graphics.FromImage(bitmap))
                {
                    g.CopyFromScreen(rect.Left, rect.Top, 0, 0, new Size(rect.Width, rect.Height), CopyPixelOperation.SourceCopy);
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
