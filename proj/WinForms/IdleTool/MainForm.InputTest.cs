namespace IdleTool
{
    using System.Diagnostics;
    using System.Runtime.InteropServices;

    partial class MainForm
    {
        #region [입력 - 선행]
        [DllImport("user32.dll", CharSet = CharSet.Auto)]
        private static extern IntPtr FindWindow(string lpClassName, string lpWindowName);

        [DllImport("user32.dll")]
        private static extern bool SetForegroundWindow(IntPtr hWnd);

        [DllImport("user32.dll")]
        private static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);

        [DllImport("user32.dll")]
        private static extern void SwitchToThisWindow(IntPtr hWnd, bool turnOn);

        [DllImport("user32.dll")]
        private static extern bool AttachThreadInput(uint idAttach, uint idAttachTo, bool fAttach);

        [DllImport("kernel32.dll")]
        private static extern uint GetCurrentThreadId();

        [DllImport("user32.dll")]
        private static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint lpdwProcessId);

        [DllImport("user32.dll", SetLastError = true)]
        private static extern uint SendInput(uint nInputs, INPUT[] pInputs, int cbSize);

        [DllImport("kernel32.dll")]
        private static extern int GetLastError();
        #endregion

        #region [입력 - 구조체]
        [StructLayout(LayoutKind.Sequential, Pack = 1)]  // 🔹 구조체 정렬 문제 해결
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

        [StructLayout(LayoutKind.Sequential, Pack = 1)] // 🔹 구조체 정렬 문제 해결
        struct KEYBDINPUT
        {
            public ushort wVk;
            public ushort wScan;
            public uint dwFlags;
            public uint time;
            public IntPtr dwExtraInfo;
        }

        private const int INPUT_KEYBOARD = 1;
        private const int KEYEVENTF_KEYUP = 0x0002;
        private const int SW_RESTORE = 9;
        #endregion

        #region [입력 - 테스트]
        void InputTest()
        {
            Console.WriteLine("🔹 메모장 찾기...");
            Process[] processes = Process.GetProcessesByName("notepad");
            if (processes.Length == 0)
            {
                Console.WriteLine("❌ 메모장을 찾을 수 없습니다.");
                return;
            }

            IntPtr hWnd = processes[0].MainWindowHandle;
            uint targetThreadId = GetWindowThreadProcessId(hWnd, out _);
            uint currentThreadId = GetCurrentThreadId();

            Console.WriteLine("🔹 창 활성화 시도...");
            ShowWindow(hWnd, SW_RESTORE);
            Thread.Sleep(100);
            SetForegroundWindow(hWnd);
            SwitchToThisWindow(hWnd, true);
            Thread.Sleep(100);

            AttachThreadInput(currentThreadId, targetThreadId, true);
            Console.WriteLine("🔹 입력 스레드 연결됨...");

            Console.WriteLine("🔹 'H' 키 입력 시도...");
            INPUT[] inputs = new INPUT[2];

            // 🔹 배열 초기화 (불필요한 값 방지)
            Array.Clear(inputs, 0, inputs.Length);

            inputs[0].type = INPUT_KEYBOARD;
            inputs[0].U.ki.wVk = 0x48;

            inputs[1].type = INPUT_KEYBOARD;
            inputs[1].U.ki.wVk = 0x48;
            inputs[1].U.ki.dwFlags = KEYEVENTF_KEYUP;

            // 🔹 크기 전달 수정
            uint result = SendInput((uint)inputs.Length, inputs, Marshal.SizeOf(typeof(INPUT)));
            if (result == 0)
            {
                int error = GetLastError();
                Console.WriteLine($"❌ SendInput 실패! 오류 코드: {error}");
            }
            else
            {
                Console.WriteLine($"✅ SendInput 성공! 입력된 키 개수: {result}");
            }

            AttachThreadInput(currentThreadId, targetThreadId, false);
            Console.WriteLine("🔹 입력 스레드 해제됨.");
        }

        void InputTest5()
        {
            Console.WriteLine("🔹 메모장 찾기...");
            Process[] processes = Process.GetProcessesByName("notepad");
            if (processes.Length == 0)
            {
                Console.WriteLine("❌ 메모장을 찾을 수 없습니다.");
                return;
            }

            IntPtr hWnd = processes[0].MainWindowHandle;
            uint targetThreadId = GetWindowThreadProcessId(hWnd, out _);
            uint currentThreadId = GetCurrentThreadId();

            Console.WriteLine("🔹 창 활성화 시도...");
            ShowWindow(hWnd, SW_RESTORE);
            Thread.Sleep(100);
            SetForegroundWindow(hWnd);
            SwitchToThisWindow(hWnd, true);
            Thread.Sleep(100);

            AttachThreadInput(currentThreadId, targetThreadId, true);
            Console.WriteLine("🔹 입력 스레드 연결됨...");

            Console.WriteLine("🔹 'H' 키 입력 시도...");
            INPUT[] inputs = new INPUT[2];

            inputs[0].type = INPUT_KEYBOARD;
            inputs[0].U.ki.wVk = 0x48;

            inputs[1].type = INPUT_KEYBOARD;
            inputs[1].U.ki.wVk = 0x48;
            inputs[1].U.ki.dwFlags = KEYEVENTF_KEYUP;

            uint result = SendInput((uint)inputs.Length, inputs, Marshal.SizeOf(typeof(INPUT)) * inputs.Length);
            if (result == 0)
            {
                int error = GetLastError();
                Console.WriteLine($"❌ SendInput 실패! 오류 코드: {error}");
                /*
                 * 5: 관리자 권한 필요
                 * 87: 잘못된 매개변수 (Marshal.SizeOf() 문제)
                 * 1400: 창 핸들이 잘못됨
                 */
            }
            else
            {
                Console.WriteLine($"✅ SendInput 성공! 입력된 키 개수: {result}");
            }

            AttachThreadInput(currentThreadId, targetThreadId, false);
            Console.WriteLine("🔹 입력 스레드 해제됨.");
        }

        void InputTest4()
        {
            Console.WriteLine("🔹 메모장 찾기...");
            Process[] processes = Process.GetProcessesByName("notepad");
            if (processes.Length == 0)
            {
                Console.WriteLine("❌ 메모장을 찾을 수 없습니다.");
                return;
            }

            IntPtr hWnd = processes[0].MainWindowHandle;
            uint targetThreadId = GetWindowThreadProcessId(hWnd, out _);
            uint currentThreadId = GetCurrentThreadId();

            Console.WriteLine("🔹 창 활성화 시도...");
            ShowWindow(hWnd, SW_RESTORE);  // 창이 최소화되어 있다면 복구
            Thread.Sleep(100);
            SetForegroundWindow(hWnd);
            SwitchToThisWindow(hWnd, true);
            Thread.Sleep(100);

            // 🔹 입력 스레드 공유 설정
            AttachThreadInput(currentThreadId, targetThreadId, true);
            Console.WriteLine("🔹 입력 스레드 연결됨...");

            // 🔹 'H' 키 입력
            Console.WriteLine("🔹 'H' 키 입력 시도...");
            INPUT[] inputs = new INPUT[2];

            // 키 누름
            inputs[0].type = INPUT_KEYBOARD;
            inputs[0].U.ki.wVk = 0x48; // 'H'

            // 키 떼기
            inputs[1].type = INPUT_KEYBOARD;
            inputs[1].U.ki.wVk = 0x48;
            inputs[1].U.ki.dwFlags = KEYEVENTF_KEYUP;

            uint result = SendInput((uint)inputs.Length, inputs, Marshal.SizeOf(typeof(INPUT)));
            Console.WriteLine($"🔹 SendInput 결과: {result}");

            // 🔹 입력 스레드 공유 해제
            AttachThreadInput(currentThreadId, targetThreadId, false);
            Console.WriteLine("🔹 입력 스레드 해제됨.");
        }

        void InputTest3()
        {
            // 🔹 대상 프로그램 찾기 (예: 메모장)
            Process[] processes = Process.GetProcessesByName("notepad");
            if (processes.Length == 0)
            {
                Console.WriteLine("메모장을 찾을 수 없습니다.");
                return;
            }

            IntPtr hWnd = processes[0].MainWindowHandle;
            uint targetThreadId = GetWindowThreadProcessId(hWnd, out _);
            uint currentThreadId = GetCurrentThreadId();

            // 🔹 입력 스레드 공유 설정
            AttachThreadInput(currentThreadId, targetThreadId, true);
            SetForegroundWindow(hWnd);
            Thread.Sleep(100); // 창이 활성화될 시간을 줌
            Console.WriteLine("Run3");

            // 🔹 'H' 키 입력
            INPUT[] inputs = new INPUT[2];

            // 키 누름
            inputs[0].type = INPUT_KEYBOARD;
            inputs[0].U.ki.wVk = 0x48; // 'H'

            // 키 떼기
            inputs[1].type = INPUT_KEYBOARD;
            inputs[1].U.ki.wVk = 0x48;
            inputs[1].U.ki.dwFlags = KEYEVENTF_KEYUP;

            SendInput((uint)inputs.Length, inputs, Marshal.SizeOf(typeof(INPUT)));

            // 🔹 입력 스레드 공유 해제
            AttachThreadInput(currentThreadId, targetThreadId, false);
        }

        void InputTest2()
        {
            // 🔹 대상 프로그램 찾기 (예: 메모장)
            Process[] processes = Process.GetProcessesByName("notepad");
            if (processes.Length == 0)
            {
                Console.WriteLine("메모장을 찾을 수 없습니다.");
                return;
            }

            IntPtr hWnd = processes[0].MainWindowHandle;

            // 🔹 창 활성화
            SetForegroundWindow(hWnd);
            Thread.Sleep(100); // 창이 활성화될 시간을 줌

            // 🔹 'H' 키 입력
            INPUT[] inputs = new INPUT[2];

            // 키 누름
            inputs[0].type = INPUT_KEYBOARD;
            inputs[0].U.ki.wVk = 0x48; // 'H'

            // 키 떼기
            inputs[1].type = INPUT_KEYBOARD;
            inputs[1].U.ki.wVk = 0x48;
            inputs[1].U.ki.dwFlags = KEYEVENTF_KEYUP;

            SendInput((uint)inputs.Length, inputs, Marshal.SizeOf(typeof(INPUT)));
        }

        void InputTest1()
        {

            //IntPtr hWnd = FindWindow(null
            //    //, "LORDNINE"

            //    //, "제목 없음 - 메모장"
            //    , "제목 없음 - Windows 메모장"
            //    ); // 창 이름으로 찾기
            //if (hWnd == IntPtr.Zero)
            //{
            //    MessageBox.Show("LORDNINE 창을 찾을 수 없습니다.");
            //    return;
            //}

            string AppName = "notepad";//notepad
            //LORDNINE
            Process[] processes = Process.GetProcessesByName(AppName);
            if (processes.Length == 0)
            {
                MessageBox.Show("메모장을 찾을 수 없습니다.");
                return;
            }

            IntPtr hWnd = processes[0].MainWindowHandle;
            if (hWnd == IntPtr.Zero)
            {
                MessageBox.Show("메모장 창을 찾을 수 없습니다.");
                return;
            }

            Console.WriteLine($"OnClick_Test4(): FindWindow= {hWnd} vs _appController= {_appController.HANDLE}");

            //hWnd = _appController.HANDLE;
            //Util.Importer.Focusing_App(hWnd);

            //PostMessage(hWnd, WM_CHAR, (IntPtr)'A', IntPtr.Zero);

            //Util.InputMachine.KEY_DOWN(hWnd, Keys.M);
            //Util.InputMachine.KEY_UP(hWnd, Keys.M);

            //Util.InputMachine.KEY_KEY(hWnd, 'M');
            //Util.InputMachine.KEY_KEY(hWnd, 'm');

            //Util.InputMachine.ActiveApp_SendKeys(hWnd, "i");

            //Util.InputMachine.Click_DOWN(hWnd, 280, 310);

            Util.Importer.Set_ForegroundWindow(hWnd);
            Thread.Sleep(100);

            Util.SENDINPUT.CustomKeyboard.Process(0, true);
            //{
            //    var apprect = _appController.Capture_Rect();
            //    int x = apprect.Left + 280;
            //    int y = apprect.Top + 310;

            //    Util.SENDINPUT.CustomMouse.Process(x, y, true);
            //}
        }
        #endregion
    }
}
