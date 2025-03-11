using System.Diagnostics;
using System.Runtime.InteropServices;

namespace IdleTool
{
    partial class MainForm
    {
        #region [입력 - Windows API 선언]
        [DllImport("user32.dll")]
        static extern bool SetForegroundWindow(IntPtr hWnd);

        [DllImport("user32.dll")]
        static extern IntPtr FindWindow(string lpClassName, string lpWindowName);

        [DllImport("user32.dll", SetLastError = true)]
        static extern uint SendInput(uint nInputs, INPUT[] pInputs, int cbSize);

        [DllImport("user32.dll")]
        static extern int GetMessageExtraInfo();
        #endregion

        #region [입력 - 구조체]
        [StructLayout(LayoutKind.Sequential)]
        struct INPUT
        {
            public int type;
            public InputUnion u;
        }

        [StructLayout(LayoutKind.Explicit)]
        struct InputUnion
        {
            [FieldOffset(0)]
            public MOUSEINPUT mi;
            [FieldOffset(0)]
            public KEYBDINPUT ki;
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

        [StructLayout(LayoutKind.Sequential)]
        struct KEYBDINPUT
        {
            public short wVk;
            public short wScan;
            public int dwFlags;
            public int time;
            public IntPtr dwExtraInfo;
        }
        #endregion

        #region [입력 - 상수값]
        // 입력 타입 상수
        const int INPUT_MOUSE = 0;
        const int INPUT_KEYBOARD = 1;

        // 키보드 이벤트 플래그
        const int KEYEVENTF_EXTENDEDKEY = 0x0001;
        const int KEYEVENTF_KEYUP = 0x0002;

        // 마우스 이벤트 플래그
        const int MOUSEEVENTF_LEFTDOWN = 0x0002;
        const int MOUSEEVENTF_LEFTUP = 0x0004;
        const int MOUSEEVENTF_RIGHTDOWN = 0x0008;
        const int MOUSEEVENTF_RIGHTUP = 0x0010;
        const int MOUSEEVENTF_ABSOLUTE = 0x8000;
        const int MOUSEEVENTF_MOVE = 0x0001;

        // 가상 키 코드
        const int VK_A = 0x41;
        const int VK_M = 0x4D;
        const int VK_RETURN = 0x0D;
        #endregion

        #region [입력 - 테스트]
        void InputTest()
        {
            //btnSendKeyboardInput_Click();
            btnSendMouseClick_Click();
        }

        IntPtr Get_TargetWindow()
        {
            const string AppName = "LORDNINE";

            Console.WriteLine("🔹 (10회차) 메모장 찾기...");
            Process[] processes = Process.GetProcessesByName(AppName);
            if (processes.Length == 0)
            {
                Console.WriteLine($"❌ {AppName}을 찾을 수 없습니다.");
                return IntPtr.Zero;
            }

            return processes[0].MainWindowHandle;
        }
        #endregion

        #region []
        private void btnSendKeyboardInput_Click()
        {
            IntPtr targetWindow = Get_TargetWindow();

            if (targetWindow != IntPtr.Zero)
            {
                // 대상 창을 포커스
                SetForegroundWindow(targetWindow);
                Thread.Sleep(500); // 창이 활성화될 시간을 줌

                // 키보드 이벤트 전송 - 여기서는 'A' 키와 Enter 키를 예시로 사용
                SendKeyboardInput(VK_M);
                Thread.Sleep(500);
                //SendKeyboardInput(VK_RETURN);

                MessageBox.Show("키보드 입력이 전송되었습니다.", "성공", MessageBoxButtons.OK, MessageBoxIcon.Information);
            }
            else
            {
                MessageBox.Show("대상 창을 찾을 수 없습니다.", "오류", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        private void btnSendMouseClick_Click()
        {
            IntPtr targetWindow = Get_TargetWindow();

            if (targetWindow != IntPtr.Zero)
            {
                // 대상 창을 포커스
                SetForegroundWindow(targetWindow);
                Thread.Sleep(500); // 창이 활성화될 시간을 줌

                // 마우스 이벤트 전송 - 화면의 특정 위치(x, y)에 클릭
                int x = 236; // 원하는 X 좌표로 변경
                int y = 300; // 원하는 Y 좌표로 변경
                SendMouseClick(x, y);

                MessageBox.Show("마우스 클릭이 전송되었습니다.", "성공", MessageBoxButtons.OK, MessageBoxIcon.Information);
            }
            else
            {
                MessageBox.Show("대상 창을 찾을 수 없습니다.", "오류", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        private void SendKeyboardInput(int keyCode)
        {
            // 키 누름 이벤트
            INPUT[] inputs = new INPUT[2];

            inputs[0].type = INPUT_KEYBOARD;
            inputs[0].u.ki.wVk = (short)keyCode;
            inputs[0].u.ki.wScan = 0;
            inputs[0].u.ki.dwFlags = 0;
            inputs[0].u.ki.time = 0;
            inputs[0].u.ki.dwExtraInfo = (IntPtr)GetMessageExtraInfo();

            // 키 뗌 이벤트
            inputs[1].type = INPUT_KEYBOARD;
            inputs[1].u.ki.wVk = (short)keyCode;
            inputs[1].u.ki.wScan = 0;
            inputs[1].u.ki.dwFlags = KEYEVENTF_KEYUP;
            inputs[1].u.ki.time = 0;
            inputs[1].u.ki.dwExtraInfo = (IntPtr)GetMessageExtraInfo();

            // 입력 전송
            SendInput(2, inputs, Marshal.SizeOf(typeof(INPUT)));
        }

        private void SendMouseClick(int x, int y)
        {
            // 화면 해상도에 맞게 좌표 변환 (MOUSEEVENTF_ABSOLUTE 플래그 사용시 필요)
            int screenWidth = Screen.PrimaryScreen.Bounds.Width;
            int screenHeight = Screen.PrimaryScreen.Bounds.Height;
            int absoluteX = (x * 65535) / screenWidth;
            int absoluteY = (y * 65535) / screenHeight;

            INPUT[] inputs = new INPUT[3];

            // 마우스 이동
            inputs[0].type = INPUT_MOUSE;
            inputs[0].u.mi.dx = absoluteX;
            inputs[0].u.mi.dy = absoluteY;
            inputs[0].u.mi.mouseData = 0;
            inputs[0].u.mi.dwFlags = MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE;
            inputs[0].u.mi.time = 0;
            inputs[0].u.mi.dwExtraInfo = (IntPtr)GetMessageExtraInfo();

            // 마우스 왼쪽 버튼 누름
            inputs[1].type = INPUT_MOUSE;
            inputs[1].u.mi.dx = 0;
            inputs[1].u.mi.dy = 0;
            inputs[1].u.mi.mouseData = 0;
            inputs[1].u.mi.dwFlags = MOUSEEVENTF_LEFTDOWN;
            inputs[1].u.mi.time = 0;
            inputs[1].u.mi.dwExtraInfo = (IntPtr)GetMessageExtraInfo();

            // 마우스 왼쪽 버튼 뗌
            inputs[2].type = INPUT_MOUSE;
            inputs[2].u.mi.dx = 0;
            inputs[2].u.mi.dy = 0;
            inputs[2].u.mi.mouseData = 0;
            inputs[2].u.mi.dwFlags = MOUSEEVENTF_LEFTUP;
            inputs[2].u.mi.time = 0;
            inputs[2].u.mi.dwExtraInfo = (IntPtr)GetMessageExtraInfo();

            // 입력 전송
            SendInput(3, inputs, Marshal.SizeOf(typeof(INPUT)));
        }
        #endregion
    }
}
