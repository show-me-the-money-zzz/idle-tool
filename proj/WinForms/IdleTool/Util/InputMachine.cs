namespace IdleTool.Util
{
    internal class InputMachine
    {
        const uint WM_KEYDOWN = 0x0100; // 키보드 입력 메시지
        const uint WM_KEYUP = 0x0101;   // 키보드 키 놓기

        #region [PostMessage]
        public static bool KEY_DOWN(IntPtr hWnd, Keys __key) => Importer.PostMessage(hWnd, WM_KEYDOWN, (IntPtr)__key, IntPtr.Zero);
        public static bool KEY_UP(IntPtr hWnd, Keys __key) => Importer.PostMessage(hWnd, WM_KEYUP, (IntPtr)__key, IntPtr.Zero);

        const uint WM_LBUTTONDOWN = 0x0201;
        const uint WM_LBUTTONUP = 0x0202;
        static IntPtr GetPosition_Click(int x, int y) => (IntPtr)((y << 16) | (x & 0xFFFF));
        public static bool Click_DOWN(IntPtr hWnd, int x, int y) => Importer.PostMessage(hWnd, WM_LBUTTONDOWN, (IntPtr)1, GetPosition_Click(x, y));
        public static bool Click_UP(IntPtr hWnd, int x, int y) => Importer.PostMessage(hWnd, WM_LBUTTONUP, IntPtr.Zero, GetPosition_Click(x, y));
        #endregion

        #region [SendMessage]
        const uint WM_CHAR = 0x0102; // 문자 입력 메시지
        public static IntPtr KEY_KEY(IntPtr hWnd, char __key) => Importer.SendMessage(hWnd, WM_CHAR, (IntPtr)__key, IntPtr.Zero);
        #endregion

        public static void ActiveApp_SendKeys(IntPtr hWnd, string __keys)
        {
            Importer.Focusing_App(hWnd);

            SendKeys.SendWait(__keys);
        }
    }
}
