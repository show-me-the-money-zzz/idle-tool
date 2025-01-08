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

            var appcontroller = new Controller.App();
            if (!appcontroller.Detect()) return;
            {//DEV TEST
                var rect = appcontroller.Capture_Rect();
                if(!rect.IsValid)
                {
                    Console.WriteLine("창 정보를 가져오는 데 실패했습니다.");
                    return;
                }
            }

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
        //    Capture_GameApp(handle, appprocess.ProcessName);

        //    LoadImage_byFileDialog();

        //    return handle;
        //}

        //static void Capture_GameApp(IntPtr __handle, string __processname)
        //{
        //    // 창의 위치 및 크기 가져오기
        //    if (GetWindowRect(__handle, out RECT rect))
        //    {
        //        int width = rect.Right - rect.Left;
        //        int height = rect.Bottom - rect.Top;

        //        Console.WriteLine($"창 위치: ({rect.Left}, {rect.Top})");
        //        Console.WriteLine($"창 크기: {width}x{height}");

        //        // 창 캡처
        //        using (Bitmap bitmap = new Bitmap(width, height))
        //        {
        //            using (Graphics g = Graphics.FromImage(bitmap))
        //            {
        //                g.CopyFromScreen(rect.Left, rect.Top, 0, 0, new Size(width, height), CopyPixelOperation.SourceCopy);
        //            }

        //            // 캡처 이미지 저장
        //            string fileName = $"{__processname}_capture.png";
        //            bitmap.Save(fileName, ImageFormat.Png);
        //            Console.WriteLine($"캡처가 완료되었습니다: {fileName}");
        //        }
        //    }
        //    else
        //    {
        //        Console.WriteLine("창 정보를 가져오는 데 실패했습니다.");
        //    }
        //}

        static void LoadImage_byFileDialog()
        {//https://tyen.tistory.com/74
            string image_file = string.Empty;

            //OpenFileDialog dialog = new OpenFileDialog();
            //dialog.InitialDirectory = @"C:\";

            //if(DialogResult.OK == dialog.ShowDialog())
            //{
            //    image_file = dialog.FileName;
            //}
            //else if(DialogResult.Cancel == dialog.ShowDialog())
            //{
            //    return;
            //}

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
