namespace IdleTool.Util
{
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
                {// 캡처 이미지 저장
                    string fileName = $"__capture__.{__processname}.png";
                    bitmap.Save(fileName, ImageFormat.Png);
                    Console.WriteLine($"캡처 이미지를 저장하였습니다: {fileName}");
                }
#endif
            }
        }
    }
}
