using System.Runtime.InteropServices;

namespace IdleTool.Util.SENDINPUT
{
    internal class CustomMouse
    {
        [StructLayout(LayoutKind.Sequential)]
        struct INPUT
        {
            public int type;
            public InputUnion U;
        }

        [StructLayout(LayoutKind.Explicit)]
        struct InputUnion
        {
            [FieldOffset(0)]
            public MOUSEINPUT mi;
        }

        [StructLayout(LayoutKind.Sequential)]
        struct MOUSEINPUT
        {
            public int dx;
            public int dy;
            public int mouseData;
            public int dwFlags;
            public int time;
            public IntPtr dwExtraInfo;
        }

        [DllImport("user32.dll", SetLastError = true)]
        private static extern uint SendInput(uint nInputs, INPUT[] pInputs, int cbSize);

        private const int INPUT_MOUSE = 0;
        private const int MOUSEEVENTF_LEFTDOWN = 0x02;
        private const int MOUSEEVENTF_LEFTUP = 0x04;

        public static uint Process(int x, int y, bool __isUP = true)
        {
            INPUT[] inputs = new INPUT[2];

            // 🔹 마우스 클릭 (왼쪽 버튼 눌림)
            inputs[0].type = INPUT_MOUSE;
            {
                inputs[0].U.mi.dx = x;
                inputs[0].U.mi.dy = y;
            }
            inputs[0].U.mi.dwFlags = MOUSEEVENTF_LEFTDOWN;

            if (__isUP)
            {
                // 🔹 마우스 클릭 (왼쪽 버튼 뗌)
                inputs[1].type = INPUT_MOUSE;
                inputs[1].U.mi.dwFlags = MOUSEEVENTF_LEFTUP;
            }

            return SendInput((uint)inputs.Length, inputs, Marshal.SizeOf(typeof(INPUT)));
        }
    }
}
