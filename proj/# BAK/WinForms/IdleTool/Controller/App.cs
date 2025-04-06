namespace IdleTool.Controller
{
    using System.Diagnostics;

    public class App
    {
        Process? _process = null;

        //public nint Handle { 
        //    get {
        //        if (null == _process) return nint.Zero;

        //        return _process.MainWindowHandle;
        //    }
        //}
        public nint HANDLE => (null == _process) ? nint.Zero : _process.MainWindowHandle;
        public int PID => (null == _process) ? 0 : _process.Id;
        public string ProcessName => (null == _process) ? "__NONE__" : _process.ProcessName;

        public Common.Types.RECT CAPT_RECT => Util.Importer.Get_AppRect(HANDLE);

        public bool Detect()
        {
            Process[] processes = Process.GetProcessesByName(Common.Defines.AppName);

            if (0 == processes.Length)
            {
                //Console.WriteLine("LORDNINE 을 실행하세요~~");
                MessageBox.Show($"{Common.Defines.AppName} 을 실행하세요 !!");
                return false;
            }

            //foreach (var process in processes)
            //{
            //    Console.WriteLine($"PID: {process.Id}, Name: {process.ProcessName}");
            //}

            _process = processes[0];

            if (nint.Zero == HANDLE)
            {
                MessageBox.Show($"{Common.Defines.AppName} 의 창이 열려있지 않아요");
                return false;
            }
            Console.WriteLine($"App Info) PID: {PID}, Name: {ProcessName}");

            return true;
        }

        public Common.Types.RECT Capture_Rect()//Get_Rect
        {
            Common.Types.RECT rect = CAPT_RECT;
            //var size = rect.Get_Size();

//#if DEBUG
//            Console.WriteLine($"창 위치: ({rect.Left}, {rect.Top})");
//            Console.WriteLine($"창 크기: {rect.Width}x{rect.Height}");

//            //if (rect.IsValid) Util.CaptureTool.NewMake(rect, "app-1st-test");
//#endif

            return rect;
        }
    }
}
