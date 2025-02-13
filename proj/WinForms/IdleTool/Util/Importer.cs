namespace IdleTool.Util
{
    using System.Runtime.InteropServices;

    internal class Importer
    {
        #region [DC]
        [DllImport("user32.dll")] static extern IntPtr GetWindowDC(IntPtr hWnd);
        [DllImport("user32.dll")] static extern int ReleaseDC(IntPtr hWnd, IntPtr hDC);

        [DllImport("user32.dll")] static extern bool SetForegroundWindow(IntPtr hWnd);

        ////
        public static IntPtr Get_DC(IntPtr __hwnd) => GetWindowDC(__hwnd);
        public static int Release_DC(IntPtr __hwnd, IntPtr __hdc) => ReleaseDC(__hwnd, __hdc);
        #endregion

        #region [WindowRect]
        [DllImport("user32.dll", SetLastError = true)] static extern bool GetWindowRect(IntPtr __hwnd, out Common.Types.RECT __rect);

        //public static bool Get_AppRect(IntPtr __hwnd, out Common.Types.RECT __rect) => GetWindowRect(__hwnd, out __rect);
        public static Common.Types.RECT Get_AppRect(IntPtr __hwnd)
        {
            Common.Types.RECT ret = new Common.Types.RECT();
            GetWindowRect(__hwnd, out ret);
            return ret;
        }
        #endregion

        public static void Focusing_App(Controller.App __app)
        {
            SetForegroundWindow(__app.HANDLE);
            System.Threading.Thread.Sleep(100);
        }
    }
}
