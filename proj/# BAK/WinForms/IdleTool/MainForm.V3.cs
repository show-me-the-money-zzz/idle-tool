using System.Diagnostics;
using System.Runtime.InteropServices;

namespace IdleTool
{
    partial class MainForm
    {
        #region [입력 - import]
        //[DllImport("user32.dll")]
        //private static extern bool SetForegroundWindow(IntPtr hWnd);

        //[DllImport("user32.dll")]
        //private static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);

        //[DllImport("user32.dll")]
        //private static extern uint SendInput(uint nInputs, IntPtr pInputs, int cbSize);

        //[DllImport("kernel32.dll")]
        //private static extern int GetLastError();
        #endregion

        #region [입력 - 구조체]
        //[StructLayout(LayoutKind.Sequential, Pack = 1)] // ✅ 구조체 크기 문제 해결 (Pack=1로 테스트)
        //struct INPUT
        //{
        //    public int type;
        //    public InputUnion U;
        //}

        //[StructLayout(LayoutKind.Explicit)]
        //struct InputUnion
        //{
        //    [FieldOffset(0)]
        //    public KEYBDINPUT ki;
        //}

        //[StructLayout(LayoutKind.Sequential, Pack = 1)] // ✅ 구조체 크기 문제 해결 (Pack=1로 테스트)
        //struct KEYBDINPUT
        //{
        //    public ushort wVk;
        //    public ushort wScan;
        //    public uint dwFlags;
        //    public uint time;
        //    public IntPtr dwExtraInfo;
        //}
        #endregion

        #region [입력 - 상수값]
        //private const int INPUT_KEYBOARD = 1;
        //private const int KEYEVENTF_KEYUP = 0x0002;
        //private const int SW_RESTORE = 9;
        #endregion

        #region [입력 - 테스트]
        void InputTest9()
        {
            //Console.WriteLine("🔹 (9회차) 메모장 찾기...");
            //Process[] processes = Process.GetProcessesByName("notepad");
            //if (processes.Length == 0)
            //{
            //    Console.WriteLine("❌ 메모장을 찾을 수 없습니다.");
            //    return;
            //}

            //IntPtr hWnd = processes[0].MainWindowHandle;

            //Console.WriteLine("🔹 창 활성화 시도...");
            //ShowWindow(hWnd, SW_RESTORE);
            //Thread.Sleep(500); // ✅ 창이 활성화될 시간을 충분히 줌

            //bool success = SetForegroundWindow(hWnd);
            //if (!success)
            //{
            //    Console.WriteLine("❌ SetForegroundWindow 실패");
            //}
            //Thread.Sleep(500);

            //Console.WriteLine("🔹 'M' 키 입력 시도...");

            //// ✅ 구조체 메모리 할당
            //int structSize = Marshal.SizeOf(typeof(INPUT));
            //IntPtr inputBuffer = Marshal.AllocHGlobal(structSize * 2);

            //try
            //{
            //    INPUT[] inputs = new INPUT[2];

            //    // ✅ 구조체 초기화 (ZeroMemory 효과)
            //    for (int i = 0; i < inputs.Length; i++)
            //    {
            //        inputs[i] = new INPUT();
            //    }

            //    inputs[0].type = INPUT_KEYBOARD;
            //    inputs[0].U.ki.wVk = 0x4D; // 'M' 키 입력

            //    inputs[1].type = INPUT_KEYBOARD;
            //    inputs[1].U.ki.wVk = 0x4D;
            //    inputs[1].U.ki.dwFlags = KEYEVENTF_KEYUP;

            //    // ✅ 구조체를 메모리에 복사
            //    Marshal.StructureToPtr(inputs[0], inputBuffer, false);
            //    Marshal.StructureToPtr(inputs[1], inputBuffer + structSize, false);

            //    // ✅ 크기 전달 방식 수정
            //    uint result = SendInput((uint)inputs.Length, inputBuffer, structSize);

            //    if (result == 0)
            //    {
            //        int error = GetLastError();
            //        Console.WriteLine($"❌ SendInput 실패! 오류 코드: {error}");
            //    }
            //    else
            //    {
            //        Console.WriteLine($"✅ SendInput 성공! 입력된 키 개수: {result}");
            //    }
            //}
            //finally
            //{
            //    Marshal.FreeHGlobal(inputBuffer); // ✅ 메모리 해제
            //}
        }
        #endregion
    }
}
