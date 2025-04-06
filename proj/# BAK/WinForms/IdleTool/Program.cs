namespace IdleTool
{
    using System;
    using System.Runtime.InteropServices;//DllImport

    internal static class Program
    {
#if DEBUG//https://maloveforme.tistory.com/286
        [DllImport("kernel32.dll", SetLastError = true)] static extern bool AllocConsole();
#endif

        //static Controller.App _appController = null;

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

            var appController = Initialize_App();
            if (null == appController)
                return;

            ApplicationConfiguration.Initialize();
            Application.Run(new MainForm(appController));
        }

        static Controller.App Initialize_App()
        {
            //if (IntPtr.Zero == Detect_GameApp()) return;

            var ret = new Controller.App();
            if (!ret.Detect()) return null;

            var app_rect = ret.Capture_Rect();
            if (!app_rect.IsValid)
            {
                Console.WriteLine("창 정보를 가져오는 데 실패했습니다.");
                return null;
            }

            return ret;
        }
    }
}
