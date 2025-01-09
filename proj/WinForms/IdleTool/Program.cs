namespace IdleTool
{
    using IdleTool.DEV;
    using System;
    //using System.Diagnostics;
    using System.Drawing;
    using System.Drawing.Imaging;
    //using System.Reflection.Metadata;

    using System.Runtime.InteropServices;//DllImport

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

        static Controller.App _appController = null;

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

            //if (!Initialize())
            //    return;

            ApplicationConfiguration.Initialize();
            Application.Run(new Form1());
        }

        static bool Initialize()
        {
            //if (IntPtr.Zero == Detect_GameApp()) return;

            _appController = new Controller.App();
            if (!_appController.Detect()) return false;

            var app_rect = _appController.Capture_Rect();
            if (!app_rect.IsValid)
            {
                Console.WriteLine("창 정보를 가져오는 데 실패했습니다.");
                return false;
            }
#if DEBUG
            //DEV.Tester0.Capture(app_controller);

            //DEV.Tester0.Open_FileDialog();

            ////PictureBox.Image = Bitmap.FromFile(image_file);
            //DEV.Tester0.Process_Local_Image();

            DEV.Tester0.Detect_IconImage_byLocal(_appController);
#endif

            return true;
        }
    }
}
