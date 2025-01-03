namespace IdleTool
{
    using System;
    using System.Diagnostics;
    using System.Runtime.InteropServices;

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

        /// <summary>
        ///  The main entry point for the application.
        /// </summary>
        [STAThread]
        static void Main()
        {
            // To customize application configuration such as set high DPI settings or default font,
            // see https://aka.ms/applicationconfiguration.

            //Console.WriteLine("Hello Winform ~~");

            if (IntPtr.Zero == Detect_GameApp()) return;

            ApplicationConfiguration.Initialize();
            Application.Run(new Form1());
        }

        const string GameAppName = "STOVE";//LORDNINE.. ex) STOVE
        static IntPtr Detect_GameApp()
        {
            Process[] processes = Process.GetProcessesByName(GameAppName);

            if (0 == processes.Length)
            {
                //Console.WriteLine("LORDNINE 을 실행하세요~~");
                MessageBox.Show($"{GameAppName} 을 실행하세요~~");
                return IntPtr.Zero;
            }

            //foreach (var process in processes)
            //{
            //    Console.WriteLine($"PID: {process.Id}, Name: {process.ProcessName}");
            //}

            Process appprocess = processes[0];
            IntPtr handle = appprocess.MainWindowHandle;

            if (IntPtr.Zero == appprocess.MainWindowHandle)
            {
                MessageBox.Show($"{GameAppName} 의 창이 열려있지 않아요");
                return IntPtr.Zero;
            }
            Console.WriteLine($"PID: {appprocess.Id}, Name: {appprocess.ProcessName}");

            if (GetWindowRect(handle, out RECT rect))
            {
                int width = rect.Right - rect.Left;
                int height = rect.Bottom - rect.Top;

                Console.WriteLine($"창 위치: ({rect.Left}, {rect.Top})");
                Console.WriteLine($"창 크기: {width}x{height}");
            }
            else
            {
                Console.WriteLine("창 정보를 가져오는 데 실패했습니다.");
            }

            return handle;
        }
    }
}