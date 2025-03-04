namespace IdleTool.Util
{
    using System.Runtime.InteropServices;

    internal class Importer
    {
        #region [COMMONs]
        [DllImport("user32.dll")] public static extern bool PostMessage(IntPtr hWnd, uint Msg, IntPtr wParam, IntPtr lParam);

        [DllImport("user32.dll")] public static extern IntPtr SendMessage(IntPtr hWnd, uint Msg, IntPtr wParam, IntPtr lParam);
        #endregion

        #region [DC]
        [DllImport("user32.dll")] static extern IntPtr GetWindowDC(IntPtr hWnd);
        [DllImport("user32.dll")] static extern IntPtr GetDC(IntPtr hWnd);
        [DllImport("user32.dll")] static extern int ReleaseDC(IntPtr hWnd, IntPtr hDC);

        [DllImport("user32.dll")] static extern bool SetForegroundWindow(IntPtr hWnd);

        ////
        public static IntPtr Get_WindowDC(IntPtr __hwnd) => GetWindowDC(__hwnd);
        public static IntPtr Get_DC(IntPtr __hwnd) => GetDC(__hwnd);
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

        public static void Focusing_App(IntPtr hWnd)
        {
            SetForegroundWindow(hWnd);
            System.Threading.Thread.Sleep(100);
        }
    }
}
