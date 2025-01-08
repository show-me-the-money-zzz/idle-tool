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
#endif

            ApplicationConfiguration.Initialize();
            Application.Run(new Form1());
        }

        //const string GameAppName = "LORDNINE";//LORDNINE.. ex) STOVE
        //static IntPtr Detect_GameApp()
        //{
        //    Process[] processes = Process.GetProcessesByName(Common.Defines.GameAppName);

        //    if (0 == processes.Length)
        //    {
        //        //Console.WriteLine("LORDNINE 을 실행하세요~~");
        //        MessageBox.Show($"{Common.Defines.GameAppName} 을 실행하세요~~");
        //        return IntPtr.Zero;
        //    }

        //    //foreach (var process in processes)
        //    //{
        //    //    Console.WriteLine($"PID: {process.Id}, Name: {process.ProcessName}");
        //    //}

        //    Process appprocess = processes[0];
        //    IntPtr handle = appprocess.MainWindowHandle;

        //    if (IntPtr.Zero == appprocess.MainWindowHandle)
        //    {
        //        MessageBox.Show($"{Common.Defines.GameAppName} 의 창이 열려있지 않아요");
        //        return IntPtr.Zero;
        //    }
        //    Console.WriteLine($"PID: {appprocess.Id}, Name: {appprocess.ProcessName}");

        //    //if (GetWindowRect(handle, out RECT rect))
        //    //{
        //    //    int width = rect.Right - rect.Left;
        //    //    int height = rect.Bottom - rect.Top;

        //    //    Console.WriteLine($"창 위치: ({rect.Left}, {rect.Top})");
        //    //    Console.WriteLine($"창 크기: {width}x{height}");
        //    //}
        //    //else
        //    //{
        //    //    Console.WriteLine("창 정보를 가져오는 데 실패했습니다.");
        //    //}

        //    LoadImage_byFileDialog();

        //    return handle;
        //}

        static void LoadImage_byFileDialog()
        {
            //PictureBox.Image = Bitmap.FromFile(image_file);
            var image1 = Load_LocalImage("icon-inventory.png");
            SaveImage_png(image1, "inventory");

            var image2 = Load_LocalImage("icon-worldmap.png");
            SaveImage_png(image2, "worldmap");
        }

        const string PublicPath = "./public";
        static string LocalPath(string __path) => $"{PublicPath}/{__path}";
        static Image? Load_LocalImage(string __path) => Bitmap.FromFile(LocalPath(__path));

        static void SaveImage_png(System.Drawing.Image? __image, string __filename)
        {
            if (null == __image) return;

            __image.Save($"{__filename}.png", ImageFormat.Png);
        }
    }
}
