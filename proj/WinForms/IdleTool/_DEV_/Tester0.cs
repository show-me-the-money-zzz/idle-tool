using Emgu.CV.CvEnum;
using Emgu.CV.Structure;
using Emgu.CV;
using IdleTool.Controller;

namespace IdleTool.DEV
{
    public static class Tester0
    {
        public static void Capture(App __app)
        {
            Bitmap capture_bitmap = null;
            string capture_filename = "__capture00__";

            capture_bitmap = Util.CaptureTool.NewMake(__app);
            //{//DC.. 캡쳐된 이미지가 갱신이 안됨
            //    capture_bitmap = Util.CaptureTool.NewMake_DC(app_controller);
            //    capture_filename = "__captureDC__";
            //}
            Util.Finder.Save_BitmapImage_PNG(capture_bitmap, capture_filename + ".app-1st-test");
        }

        public static void Open_FileDialog()
        {
            string filedialog_initial_dir = string.Empty;
            filedialog_initial_dir = @"D:\";
            Util.Finder.Open_FileDialog(filedialog_initial_dir);
        }

        public static void Process_Local_Image()
        {
            var image1 = Util.Finder.Load_LocalImage("icon-inventory.png");
            Util.Finder.Save_LocalImage_PNG(image1, "inventory");

            var image2 = Util.Finder.Load_LocalImage("icon-worldmap.png");
            Util.Finder.Save_Image_PNG(image2, "worldmap");
        }

        public static void Detect_IconImage_byLocal(App __app)
        {
            string local_imaage = "icon-worldmap";

            var bmp_app = Util.CaptureTool.NewMake(__app);
            var bmp_icon = (Bitmap)Util.Finder.Load_LocalImage(local_imaage + ".png");
            //#data\\Image To Bitmap 변환.md 참고

            var mat_app = Util.GFX.Bitmap_To_Mat_Direct(bmp_app);
            var mat_icon = Util.GFX.Bitmap_To_Mat_Direct(bmp_icon);

            // 결과 매트릭스 생성
            Mat result = new Mat();
            CvInvoke.MatchTemplate(mat_app, mat_icon, result, TemplateMatchingType.CcorrNormed);

            // 결과에서 가장 유사한 위치 찾기
            double minVal = 0, maxVal = 0;
            Point minLoc = new Point();
            Point maxLoc = new Point();
            CvInvoke.MinMaxLoc(result, ref minVal, ref maxVal, ref minLoc, ref maxLoc);

#if DEBUG
            {//Console.WriteLine.. 템플릿 위치 표시
                Console.WriteLine($"템플릿 위치(MaxLoc): X={maxLoc.X}, Y={maxLoc.Y} (MinLoc= {minLoc.X}, {minLoc.Y})");
                //Console.WriteLine($"템플릿 영역: {maxLoc.X}, {maxLoc.Y} ~ {maxLoc.X + mat_icon.Width}, {maxLoc.Y + mat_icon.Height}");
                Console.WriteLine($"유사도: {maxVal}");
            }
#endif

            // 일치하는 위치에 사각형 그리기
            Rectangle matchRect = new Rectangle(maxLoc, new Size(mat_icon.Width, mat_icon.Height));
            CvInvoke.Rectangle(mat_app, matchRect, new MCvScalar(0, 255, 0), 3);

            // 결과 이미지를 저장 (선택)
            Point clickPoint = maxLoc;//클릭 위치
            {
                clickPoint.X += (int)(mat_icon.Width * 0.5f);
                clickPoint.Y += (int)(mat_icon.Height * 0.5f);
            }

            {//captured local save
                //string outputPath = $@".\matched_{local_imaage} ({maxLoc.X}, {maxLoc.Y} ~ {maxLoc.X + mat_icon.Width}, {maxLoc.Y + mat_icon.Height}).png";
                string outputPath = $@".\matched_{local_imaage} ({clickPoint.X}, {clickPoint.Y}).png";
                mat_app.Save(outputPath);

#if DEBUG
                Console.WriteLine($"결과 이미지가 저장되었습니다: {outputPath}");
#endif
            }
        }
    }
}
