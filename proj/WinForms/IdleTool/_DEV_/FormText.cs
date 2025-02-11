using System;

namespace IdleTool.DEV
{
    using IdleTool.Controller;
    using System.Runtime.InteropServices;
    using System.Text;
    using System.Windows.Forms;

    internal class FormText
    {
        [DllImport("user32.dll", SetLastError = true)]
        private static extern IntPtr FindWindow(string lpClassName, string lpWindowName);
        [DllImport("user32.dll", SetLastError = true)]
        private static extern IntPtr FindWindowEx(IntPtr hWndParent, IntPtr hWndChildAfter, string lpszClass, string lpszWindow);

        [DllImport("user32.dll", SetLastError = true, CharSet = CharSet.Auto)]
        private static extern int GetWindowText(IntPtr hWnd, StringBuilder lpString, int nMaxCount);

        public static string Find_TextEdit()
        {
            // 대상 프로그램의 창 제목
            IntPtr hwnd = FindWindow(null, Common.Defines.AppName);
            if (hwnd == IntPtr.Zero)
            {
#if DEBUG
                Console.WriteLine("창을 찾을 수 없음");
#endif
                return string.Empty;
            }

            //텍스트 영역 찾기
            IntPtr editHwnd = FindWindowEx(hwnd, IntPtr.Zero, "Edit", null);
            if (editHwnd == IntPtr.Zero)
            {
#if DEBUG
                Console.WriteLine("텍스트 영역을 찾을 수 없음");
#endif
                return string.Empty;
            }
            Console.WriteLine("텍스트 영역 찾았다 !!");

            // 텍스트 가져오기
            StringBuilder sb = new StringBuilder(256);
            GetWindowText(editHwnd, sb, sb.Capacity);

            return sb.ToString();
        }
    }
}
