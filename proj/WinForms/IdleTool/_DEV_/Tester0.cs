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
            var bmp_app = Util.CaptureTool.NewMake(__app);
            var bmp_icon_worldmap = (Bitmap)Util.Finder.Load_LocalImage("icon-inventory.png");
            //#data\\Image To Bitmap 변환.md 참고

            var mat_app = Util.GFX.Bitmap_To_Mat_Direct(bmp_app);
            var mat_icon_worldmap = Util.GFX.Bitmap_To_Mat_Direct(bmp_icon_worldmap);

            // 결과 매트릭스 생성
            Mat result = new Mat();
            CvInvoke.MatchTemplate(mat_app, mat_icon_worldmap, result, TemplateMatchingType.CcorrNormed);

            // 결과에서 가장 유사한 위치 찾기
            double minVal = 0, maxVal = 0;
            Point minLoc = new Point();
            Point maxLoc = new Point();
            CvInvoke.MinMaxLoc(result, ref minVal, ref maxVal, ref minLoc, ref maxLoc);

            // 템플릿 위치 표시
            Console.WriteLine($"템플릿 위치: X={maxLoc.X}, Y={maxLoc.Y}");
            Console.WriteLine($"유사도: {maxVal}");

            // 일치하는 위치에 사각형 그리기
            Rectangle matchRect = new Rectangle(maxLoc, new Size(mat_icon_worldmap.Width, mat_icon_worldmap.Height));
            CvInvoke.Rectangle(mat_app, matchRect, new MCvScalar(0, 255, 0), 3);

            // 결과 이미지를 저장 (선택)
            string outputPath = @".\matched_result.png";
            mat_app.Save(outputPath);
            Console.WriteLine($"결과 이미지가 저장되었습니다: {outputPath}");
        }
    }
}
