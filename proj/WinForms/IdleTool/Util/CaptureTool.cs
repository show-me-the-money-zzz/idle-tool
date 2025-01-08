namespace IdleTool.Util
{
    using System.Drawing;
    using System.Drawing.Imaging;

    public static class CaptureTool
    {
        public static void NewMake(Common.Types.RECT __rect, string __processname)
        {
            using (Bitmap bitmap = new Bitmap(__rect.Width, __rect.Height))
            {
                using (Graphics g = Graphics.FromImage(bitmap))
                {
                    g.CopyFromScreen(__rect.Left, __rect.Top, 0, 0, new Size(__rect.Width, __rect.Height), CopyPixelOperation.SourceCopy);
                }

#if DEBUG
                Save_Bitmap_PNG(bitmap, $"__capture__.{__processname}");
#endif
            }
        }

        public static void Save_Bitmap_PNG(Bitmap __bitmap, string __path)
        {
            string fileName = $"{__path}.png";
            __bitmap.Save(fileName, ImageFormat.Png);
            Console.WriteLine($"캡처 이미지를 저장하였습니다: {fileName}");
        }
    }
}
