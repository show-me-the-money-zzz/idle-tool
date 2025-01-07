namespace IdleTool.Controller
{
    using System.Diagnostics;
    using System.Drawing.Imaging;

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

            //if (Util.Importer.Get_AppRect(Handle, out Common.Types.RECT rect))
            //{
            //    int width = rect.Right - rect.Left;
            //    int height = rect.Bottom - rect.Top;

            //    Console.WriteLine($"App Info) 위치: ({rect.Left}, {rect.Top})");
            //    Console.WriteLine($"App Info) 크기: {width}x{height}");
            //}
            //else
            //{
            //    Console.WriteLine("창 정보를 가져오는 데 실패했습니다.");
            //}

            return true;
        }

        public void Capture()
        {
            // 창의 위치 및 크기 가져오기
            if (Util.Importer.Get_AppRect(HANDLE, out Common.Types.RECT rect))
            {
                int width = rect.Right - rect.Left;
                int height = rect.Bottom - rect.Top;

                Console.WriteLine($"창 위치: ({rect.Left}, {rect.Top})");
                Console.WriteLine($"창 크기: {width}x{height}");

                // 창 캡처
                using (Bitmap bitmap = new Bitmap(width, height))
                {
                    using (Graphics g = Graphics.FromImage(bitmap))
                    {
                        g.CopyFromScreen(rect.Left, rect.Top, 0, 0, new Size(width, height), CopyPixelOperation.SourceCopy);
                    }

                    {// 캡처 이미지 저장
                        string fileName = $"__capture__{ProcessName}.png";
                        bitmap.Save(fileName, ImageFormat.Png);
                        Console.WriteLine($"캡처가 완료되었습니다: {fileName}");
                    }
                }
            }
            else
            {
                Console.WriteLine("창 정보를 가져오는 데 실패했습니다.");
            }
        }
    }
}
