namespace IdleTool
{
    using System;
    //using System.Diagnostics;
    using System.Drawing;
    using System.Drawing.Imaging;
    //using System.Reflection.Metadata;

#if DEBUG
    using System.Runtime.InteropServices;
#endif

    internal static class Program
    {
        [DllImport("user32.dll", SetLastError = true)]
        private static extern bool GetWindowRect(IntPtr hWnd, out RECT lpRect);
        [StructLayout(LayoutKind.Sequential)]
        public struct RECT
        {
            public int Left;
            public int Top;
            public int Right;
            public int Bottom;
        }

#if DEBUG//https://maloveforme.tistory.com/286
        [DllImport("kernel32.dll", SetLastError = true)] static extern bool AllocConsole();
#endif

        /// <summary>
        ///  The main entry point for the application.
        /// </summary>
        [STAThread]
        static void Main()
        {
            // To customize application configuration such as set high DPI settings or default font,
            // see https://aka.ms/applicationconfiguration.

            //Console.WriteLine("Hello Winform ~~");

#if DEBUG
            AllocConsole();
#endif

            //if (IntPtr.Zero == Detect_GameApp()) return;

            var app_controller = new Controller.App();
            if (!app_controller.Detect()) return;

            var app_rect = app_controller.Capture_Rect();
            if(!app_rect.IsValid)
            {
                Console.WriteLine("창 정보를 가져오는 데 실패했습니다.");
                return;
            }
#if DEBUG
            {//DEV TEST.. Capture
                Bitmap capture_bitmap = null;
                string capture_filename = "__capture00__";

                capture_bitmap = Util.CaptureTool.NewMake(app_controller);
                //{//DC.. 캡쳐된 이미지가 갱신이 안됨
                //    capture_bitmap = Util.CaptureTool.NewMake_DC(app_controller);
                //    capture_filename = "__captureDC__";
                //}
                Util.CaptureTool.Save_Bitmap_PNG(capture_bitmap, capture_filename + ".app-1st-test");
            }

            //{//DEV TEST.. Open_FileDialog
            //    string filedialog_initial_dir = string.Empty;
            //    filedialog_initial_dir = @"D:\";
            //    Util.Finder.Open_FileDialog(filedialog_initial_dir);
            //}

            //{//DEV TEST.. Load Local Image
            //    //PictureBox.Image = Bitmap.FromFile(image_file);

            //    var image1 = Util.Finder.Load_LocalImage("icon-inventory.png");
            //    Util.Finder.Save_LocalImage_PNG(image1, "inventory");

            //    var image2 = Util.Finder.Load_LocalImage("icon-worldmap.png");
            //    Util.Finder.Save_Image_PNG(image2, "worldmap");
            //}
#endif

            ApplicationConfiguration.Initialize();
            Application.Run(new Form1());
        }
    }
}
