namespace IdleTool.Util
{
    using System.Runtime.InteropServices;

    internal class Importer
    {
        #region [COMMONs]
        [DllImport("user32.dll")] static extern bool PostMessage(IntPtr hWnd, uint Msg, IntPtr wParam, IntPtr lParam);

        [DllImport("user32.dll")] static extern IntPtr SendMessage(IntPtr hWnd, uint Msg, IntPtr wParam, IntPtr lParam);
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

        #region [INPUT KEYBOARD]
        const uint WM_KEYDOWN = 0x0100; // 키보드 입력 메시지
        const uint WM_KEYUP = 0x0101;   // 키보드 키 놓기

        public static bool KEY_DOWN(IntPtr hWnd, Keys __key) => PostMessage(hWnd, WM_KEYDOWN, (IntPtr)__key, IntPtr.Zero);
        public static bool KEY_UP(IntPtr hWnd, Keys __key) => PostMessage(hWnd, WM_KEYUP, (IntPtr)__key, IntPtr.Zero);

        //SendMessage
        const uint WM_CHAR = 0x0102; // 문자 입력 메시지
        public static IntPtr KEY_KEY(IntPtr hWnd, char __key) => SendMessage(hWnd, WM_CHAR, (IntPtr)__key, IntPtr.Zero);

        public static void ActiveApp_SendKeys(IntPtr hWnd, string __keys)
        {
            Focusing_App(hWnd);

            SendKeys.SendWait(__keys);
        }
        #endregion

        public static void Focusing_App(IntPtr hWnd)
        {
            SetForegroundWindow(hWnd);
            System.Threading.Thread.Sleep(100);
        }
    }
}
