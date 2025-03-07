namespace ProcessChecker
{
    using System.Diagnostics;
    using System.Security.Principal;

    internal static class Program
    {
        /// <summary>
        ///  The main entry point for the application.
        /// </summary>
        [STAThread]
        static void Main()
        {

            if (!IsAdministrator())
            {
                // 현재 관리자 권한이 아니라면, 관리자 권한으로 재실행
                RestartAsAdmin();
                return;
            }

            MessageBox.Show("관리자 권한으로 실행되었습니다!", "알림", MessageBoxButtons.OK, MessageBoxIcon.Information);

            // To customize application configuration such as set high DPI settings or default font,
            // see https://aka.ms/applicationconfiguration.
            ApplicationConfiguration.Initialize();
            Application.Run(new Form1());
        }

        static bool IsAdministrator()
        {
            using (WindowsIdentity identity = WindowsIdentity.GetCurrent())
            {
                WindowsPrincipal principal = new WindowsPrincipal(identity);
                return principal.IsInRole(WindowsBuiltInRole.Administrator);
            }
        }

        static void RestartAsAdmin()
        {
            var startInfo = new ProcessStartInfo
            {
                FileName = Process.GetCurrentProcess().MainModule.FileName,
                UseShellExecute = true,
                Verb = "runas" // 관리자 권한으로 실행
            };

            try
            {
                Process.Start(startInfo);
                Environment.Exit(0); // 기존 프로세스 종료
            }
            catch
            {
                Console.WriteLine("관리자 권한 실행이 취소되었습니다.");
            }
        }
    }
}