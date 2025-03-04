using System.Runtime.InteropServices;

namespace IdleTool.Util.SENDINPUT
{
    internal class CustomKeyboard
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
            public KEYBDINPUT ki;
        }

        [StructLayout(LayoutKind.Sequential)]
        struct KEYBDINPUT
        {
            public ushort wVk;
            public ushort wScan;
            public uint dwFlags;
            public uint time;
            public IntPtr dwExtraInfo;
        }

        [DllImport("user32.dll", SetLastError = true)]
        private static extern uint SendInput(uint nInputs, INPUT[] pInputs, int cbSize);

        private const int INPUT_KEYBOARD = 1;
        private const int KEYEVENTF_KEYUP = 0x0002;

        public static uint Process(ushort __key, bool __isKeyup = true)
        {
            { __key = 0x4D; }// 'M' 키 코드

            INPUT[] inputs = new INPUT[2];

            //누르기
            inputs[0].type = INPUT_KEYBOARD;
            inputs[0].U.ki.wVk = __key;

            if (__isKeyup)
            {
                //떼기
                inputs[1].type = INPUT_KEYBOARD;
                inputs[1].U.ki.wVk = __key;
                inputs[1].U.ki.dwFlags = KEYEVENTF_KEYUP;
            }

            return SendInput((uint)inputs.Length, inputs, Marshal.SizeOf(typeof(INPUT)));
        }
    }
}
