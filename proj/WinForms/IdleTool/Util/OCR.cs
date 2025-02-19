namespace IdleTool.Util
{
    using Emgu.CV.OCR;
    using Emgu.CV.Structure;
    using Emgu.CV;
    using Tesseract;
    using Emgu.CV.CvEnum;

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
                var filterBitmap = Filter_Color(croppedBitmap, __filename);

                //{//노이즈 제거.. MedianBlur가 작은 커널 크기에서는 경계를 유지하지 못하기 때문에 부적절
                //    var remove_noise = Remove_Noise(croppedBitmap, __filename);

                //    if (!string.IsNullOrEmpty(__filename))
                //        remove_noise.Save($"./noise-{__filename} ({__region.X}, {__region.Y}) ({__region.Width} x {__region.Height}).png");
                //}

                if (!string.IsNullOrEmpty(__filename))
                {
                    var mat_app = Util.GFX.Bitmap_To_Mat_Direct(croppedBitmap);

                    //// 1. 노이즈 제거 (Gaussian Blur 적용)
                    //Mat denoisedImage = new Mat();
                    //CvInvoke.GaussianBlur(mat_app, denoisedImage, new System.Drawing.Size(5, 5), 1.5);

                    //// 2. 색 반전
                    //Mat invertedImage = new Mat();
                    //CvInvoke.BitwiseNot(mat_app, invertedImage);

                    mat_app.Save($"./OCRRead-{__filename} ({__region.X}, {__region.Y}) ({__region.Width} x {__region.Height}).png");
                }

                //// Bitmap을 Pix로 변환
                //using (Pix img = ConvertBitmapToPix(filterBitmap))
                {
                    ret = Process_Tesseract(filterBitmap, __isNumber, __filename);
                    //ret = Process_Tesseract2(filterBitmap, __isNumber, __filename);
                }
            }

            return ret;
        }

        static Bitmap Filter_Color(Bitmap __srcBitmap, string __filename = "")
        {
            Mat mat = Util.GFX.Bitmap_To_Mat_Direct(__srcBitmap);

            // ! BGR -> HSV 변환
            Mat hsvImage = new Mat();
            CvInvoke.CvtColor(mat, hsvImage, Emgu.CV.CvEnum.ColorConversion.Bgr2Hsv);

            // ! 흰색 계열 필터링 (HSV 범위 설정) (흰색 계열 마스크 생성)
            Mat mask = new Mat();
            CvInvoke.InRange(hsvImage,
                new ScalarArray(new MCvScalar(0, 0, 200)),  // 하한값 (H=0, S=0, V=200)
                new ScalarArray(new MCvScalar(180, 50, 255)), // 상한값 (H=180, S=50, V=255)
                mask);
            //{
            //    ////파란색 계열 필터링
            //    CvInvoke.InRange(hsvImage,
            //        new ScalarArray(new MCvScalar(100, 50, 50)), // 하한 (H, S, V)
            //        new ScalarArray(new MCvScalar(140, 255, 255)), // 상한 (H, S, V)
            //        mask);
            //}

            //{// ! 팽창(Dilation) 연산 적용 (글자 두께 증가)
            //    Mat dilatedMask = new Mat();
            //    Mat kernel = CvInvoke.GetStructuringElement(ElementShape.Rectangle, new System.Drawing.Size(3, 3), new System.Drawing.Point(-1, -1));
            //    CvInvoke.Dilate(mask, dilatedMask, kernel, new System.Drawing.Point(-1, -1), 2, BorderType.Default, new MCvScalar(0));
            //}

            // ! 원본 이미지에서 흰색 부분만 추출
            /* 이 연산의 의미:
             *  mask에서 255(흰색)인 부분만 유지하고, 나머지는 0(검은색)으로 변환
             *  즉, image의 흰색 계열 부분만 남기고 나머지는 제거
             */
            Mat result = new Mat();
            CvInvoke.BitwiseAnd(mat, mat, result, mask);
            /*
                * 첫 번째 인자 (image): 원본 이미지 (BGR 형식)
            두 번째 인자 (image): 원본 이미지와 동일한 이미지 (이항 연산이므로 필요)
            세 번째 인자 (result): 결과 이미지 (흰색 부분만 추출된 이미지)
            네 번째 인자 (mask): 흰색이 유지될 부분을 지정한 마스크 이미지 (흰색 영역: 255, 나머지: 0)
                */

            //{//배경 파란색 처리
            //    // ! 배경을 파란색으로 변경 (마스크 반전 후 적용)
            //    Mat background = new Mat(mat.Size, DepthType.Cv8U, 3);
            //    background.SetTo(new MCvScalar(255, 0, 0)); // 파란색 (BGR: 255, 0, 0)

            //    Mat invertedMask = new Mat();
            //    CvInvoke.BitwiseNot(mask, invertedMask); // 마스크 반전

            //    Mat blueBackground = new Mat();
            //    CvInvoke.BitwiseAnd(background, background, blueBackground, invertedMask); // 파란 배경 적용

            //    // ! 흰색만 유지된 이미지와 파란색 배경 합성
            //    Mat finalResult = new Mat();
            //    CvInvoke.Add(result, blueBackground, finalResult);
            //}

            if (!string.IsNullOrEmpty(__filename))
                CvInvoke.Imwrite($"./filterd_{__filename}.png", result);// 5. 필터링된 이미지 저장

            return Util.GFX.Mat_To_Bitmap(result);
        }

        static Mat Remove_Noise(Bitmap __bitmap, string __filename = "")
        {
            Mat mat = Util.GFX.Bitmap_To_Mat_Direct(__bitmap);
            Mat hsvImage = new Mat();
            const int Ksize = 3;
            /*
             * 3: 약한 노이즈 제거 (경계 유지)
             * 5: 중간 정도 노이즈 제거
             * 7: 더 강한 노이즈 제거 (텍스트 경계 약간 흐려질 수 있음)
             * 9: 이상	강한 블러 효과 (텍스트 가독성 저하 가능)
             */
            CvInvoke.MedianBlur(mat, hsvImage, Ksize);

            return hsvImage;
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

        //using IronOcr;
        //public static string Read_Text_byCaptured_IronOCR(Bitmap __bitmap, Rectangle __region)
        //{
        //    var ocr = new IronTesseract();

        //    using (Bitmap croppedBitmap = Util.GFX.CropBitmap(__bitmap, __region))
        //    {
        //        using (var input = new OcrInput(croppedBitmap))
        //        {
        //            input.DeNoise();          // 이미지 노이즈 제거
        //            input.Deskew();           // 이미지 정렬 (기울어진 텍스트 수정)
        //            input.Invert();           // 색 반전 (흰 배경, 검은 글씨로 변경)

        //            OcrResult result = ocr.Read(input);
        //            Console.WriteLine(result.Text);
        //        }
        //    }

        //    //{
        //    //    using (var input = new OcrInput())
        //    //    {
        //    //        input.LoadImage(croppedBitmap);
        //    //        {
        //    //            input.DeNoise();          // 이미지 노이즈 제거
        //    //                                      //input.Deskew();           // 이미지 정렬 (기울어진 텍스트 수정)
        //    //                                      //input.Invert();           // 색 반전 (흰 배경, 검은 글씨로 변경)
        //    //        }
        //    //        var result = ocr.Read(input);
        //    //        //ret = result.Text;
        //    //    }

        //    //}
        //    return "";
        //}
    }
}
