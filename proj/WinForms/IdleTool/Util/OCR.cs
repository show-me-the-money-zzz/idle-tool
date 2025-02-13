namespace IdleTool.Util
{
    using Emgu.CV.OCR;
    using Emgu.CV.Structure;
    using Emgu.CV;
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

        public static string Read_Text_byCaptured(Bitmap __bitmap, Rectangle __region, bool __isNumber = true, string __filename = "")
        {
            string ret = "";

            // 특정 영역 잘라내기
            using (Bitmap croppedBitmap = Util.GFX.CropBitmap(__bitmap, __region))
            {
                if (!string.IsNullOrEmpty(__filename))
                {
                    var mat_app = Util.GFX.Bitmap_To_Mat_Direct(croppedBitmap);
                    mat_app.Save($"./OCRRead-{__filename} ({__region.X}, {__region.Y}) ({__region.Width} x {__region.Height}).png");
                }

                // Bitmap을 Pix로 변환
                //using (Pix img = ConvertBitmapToPix(croppedBitmap))
                {
                    ret = Process_Tesseract(croppedBitmap, __isNumber, __filename);
                    //ret = Process_Tesseract2(croppedBitmap, __isNumber, __filename);
                }
            }

            return ret;
        }

        const string Path_Tessdata = @"./tessdata";
        static string Get_Langs()
        {
            var ret = "eng+kor+kor_vert";
            //{
            //    Langs = "kor";
            //    Langs = "kor_vert";
            //    Langs = "kor+kor_vert";
            //}
            return ret;
        }
        static string Process_Tesseract(Bitmap __bitmap, bool __isNumber, string __tag)
        {
            string ret = "";

            using (var engine = new TesseractEngine(Path_Tessdata, Get_Langs(), EngineMode.Default))
            {
                if (__isNumber)
                    engine.SetVariable("tessedit_char_whitelist", "0123456789,./");

                var page = engine.Process(PixConverter.ToPix(__bitmap));

                ret = page.GetText().Trim();

                if (!string.IsNullOrEmpty(__tag))
                    Console.WriteLine($"OCR({__tag}): {ret}");
            }

            return ret;
        }
        static string Process_Tesseract2(Bitmap __bitmap, bool __isNumber, string __tag)
        {
            string ret = "";

            //using (Tesseract ocr = new Tesseract(@"C:\Program Files\Tesseract-OCR\tessdata", "eng", OcrEngineMode.TesseractLstmCombined))
            //{
            //    Image<Bgr, byte> img = new Image<Bgr, byte>(image);
            //    ocr.SetImage(img);
            //    ocr.Recognize();
            //    return ocr.GetUTF8Text();
            //}
            using (Tesseract ocr = new Tesseract(Path_Tessdata, Get_Langs(), OcrEngineMode.TesseractLstmCombined))
            {
                Mat mat = Util.GFX.Bitmap_To_Mat_Direct(__bitmap);
                //Image<Bgr, byte> img = new Image<Bgr, byte>(croppedBitmap);                        
                Image<Bgr, byte> img = mat.ToImage<Bgr, byte>();
                ocr.SetImage(img);
                ocr.Recognize();
                ret = ocr.GetUTF8Text();

                ret = ret.Replace("\r\n", ""); // "\r\n" 제거

                if (!string.IsNullOrEmpty(__tag))
                    Console.WriteLine($"OCR({__tag}): {ret}");
            }

            return ret;
        }
    }
}
