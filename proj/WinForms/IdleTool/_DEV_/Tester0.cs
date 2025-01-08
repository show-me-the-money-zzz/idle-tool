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
            Util.CaptureTool.Save_Bitmap_PNG(capture_bitmap, capture_filename + ".app-1st-test");
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
    }
}
