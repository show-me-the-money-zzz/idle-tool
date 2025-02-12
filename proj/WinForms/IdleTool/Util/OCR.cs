using System;
using System.Drawing;
using System.Drawing.Imaging;
using System.IO;

namespace IdleTool.Util
{
    using IdleTool.Controller;
    using Tesseract;

    internal class OCR
    {
        //public static string foo2(App __app)
        //{
        //    var bmp_app = Util.CaptureTool.NewMake(__app);

        //    Rectangle captureArea = new Rectangle(538, 1043, 86, 22); // 특정 영역 지정
        //    using (Graphics g = Graphics.FromImage(bmp_app))
        //    {
        //        g.CopyFromScreen(captureArea.Location, Point.Empty, captureArea.Size);
        //    }
        //    {
        //        var mat_app = Util.GFX.Bitmap_To_Mat_Direct(bmp_app);
        //        mat_app.Save($"./OCRRead ({captureArea.X}, {captureArea.Y}) ({captureArea.Width} x {captureArea.Height}).png");
        //    }

        //    using (var engine = new TesseractEngine(@"./tessdata", "eng", EngineMode.Default))
        //    {
        //        var page = engine.Process(PixConverter.ToPix(bmp_app));

        //        Console.WriteLine($"OCR: {page}");
        //    }

        //    return "";
        //}

        public static string Read_Text(App __app, Rectangle __region, bool __isNumber = true, string __filename = "")
        {
            string ret = "";

            var bmp_app = Util.CaptureTool.NewMake(__app);

            // 특정 영역 잘라내기
            using (Bitmap croppedBitmap = CropBitmap(bmp_app, __region))
            {
                if(!string.IsNullOrEmpty(__filename))
                {
                    var mat_app = Util.GFX.Bitmap_To_Mat_Direct(croppedBitmap);
                    mat_app.Save($"./OCRRead-{__filename} ({__region.X}, {__region.Y}) ({__region.Width} x {__region.Height}).png");
                }

                // Bitmap을 Pix로 변환
                //using (Pix img = ConvertBitmapToPix(croppedBitmap))
                {
                    var Langs = "eng+kor+kor_vert";
                    //{
                    //    Langs = "kor";
                    //    Langs = "kor_vert";
                    //    Langs = "kor+kor_vert";
                    //}
                    using (var engine = new TesseractEngine(@"./tessdata", Langs, EngineMode.Default))
                    {
                        if(__isNumber)
                            engine.SetVariable("tessedit_char_whitelist", "0123456789,./");

                        var page = engine.Process(PixConverter.ToPix(croppedBitmap));

                        ret = page.GetText().Trim();

                        if (!string.IsNullOrEmpty(__filename))
                            Console.WriteLine($"OCR({__filename}): {ret}");
                    }
                }
            }

            if (__isNumber)
                ret = ret.Replace(",", "");

            return ret;
        }

        /// <summary>
        /// 특정 영역을 잘라서 새로운 Bitmap 생성
        /// </summary>
        static Bitmap CropBitmap(Bitmap source, Rectangle region)
        {
            Bitmap cropped = new Bitmap(region.Width, region.Height);
            using (Graphics g = Graphics.FromImage(cropped))
            {
                g.DrawImage(source, new Rectangle(0, 0, region.Width, region.Height), region, GraphicsUnit.Pixel);
            }
            return cropped;
        }

        ///// <summary>
        ///// PixConverter 없이 Bitmap을 Pix로 변환
        ///// </summary>
        //static Pix ConvertBitmapToPix(Bitmap bmp)
        //{
        //    using (MemoryStream ms = new MemoryStream())
        //    {
        //        bmp.Save(ms, ImageFormat.Png); // PNG 형식으로 저장 후 메모리에 로드
        //        ms.Position = 0;
        //        return Pix.LoadFromMemory(ms.ToArray());
        //    }
        //}
    }
}
