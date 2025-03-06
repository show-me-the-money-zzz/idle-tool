namespace IdleTool
{
    using IdleTool.Controller;
    using System.Diagnostics;
    using System.Drawing;
    using System.Runtime.InteropServices;
    using System.Windows.Forms;

    public partial class MainForm : Form
    {
        Controller.App _appController = null;
        Controller.StatBar _statbar = new Controller.StatBar();

        public MainForm(Controller.App __app)
        {
            InitializeComponent();

            Load_Data();

            KeyPreview = true;//키 입력 안 먹을 때
            //https://free-sounds.tistory.com/39

            _appController = __app;
            Setup_Title(__app);
            //{ Test_App(); }//DEV TEST
            Util.Importer.Focusing_App(__app.HANDLE);

            {
                //foreach (ToolStripItem item in statusStrip.Items)
                //    Console.WriteLine($"아이템: {item.Text}, 타입: {item.GetType()}");
                //statusStrip.SizingGrip = true;
                //statusStrip.Refresh();

                statusLabel_State.Text = "게임 찾기 성공!!";
            }
            _statbar.Setup(__app
                , statusLabel_HP, statusLabel_MP
                , statusLabel_Potion
                , statusLabel_State
                );
        }

        void Load_Data()
        {
            {//Text Area
                var json = Util.Finder.Read_JsonData_Textarea();
#if DEBUG
                Console.WriteLine($"[{json.Count}] {json.ToString()}");
#endif
                foreach (var item in json)
                {
                    string key = item.Key;
                    var val = (item.Value).ToString().Split(",");
                    {
                        var rectangle = new Rectangle();
                        {
                            rectangle.X = int.Parse(val[0]);
                            rectangle.Y = int.Parse(val[1]);
                            rectangle.Width = int.Parse(val[2]);
                            rectangle.Height = int.Parse(val[3]);
                        }
                        Common.Stores.Instance.List_TextArea.Add(key, rectangle);
                    }
                };
#if DEBUG
                //int index = 0;
                //foreach (var item in Common.Stores.Instance.List_TextArea)
                //    Console.WriteLine($"[{index++}] {item}");
#endif
            }
        }

        void Setup_Title(Controller.App __app)
        {
            string title = "쇼미더머니";
            title += $" - {Common.Defines.AppName}";
            {
                var rect = __app.Capture_Rect();
                title += $" |   위치: {rect.Left}, {rect.Top}";
                title += $" |   크기: {rect.Width} x {rect.Height}";
            }

            this.Text = title;
        }

        void Test_App()
        {
            //DEV.Tester0.Capture(_appController);

            //DEV.Tester0.Open_FileDialog();

            //PictureBox.Image = Bitmap.FromFile(image_file);
            //DEV.Tester0.Process_Local_Image();

            //DEV.Tester0.Detect_IconImage_byLocal(_appController);
        }

        private void OnClick_Test1(object sender, EventArgs e)
        {
            //_count += 1;
            //TXT_Logger.Text = $"클릭 {_count}\r\n테스트";

            Log_DetectResult(DEV.Tester0.Detect_IconImage_byLocal(_appController, "icon-worldmap"));
        }
        private void OnClick_Test2(object sender, EventArgs e)
        {
            Log_DetectResult(DEV.Tester0.Detect_IconImage_byLocal(_appController, "icon-inventory"));
        }
        private void OnClick_Test3(object sender, EventArgs e)
        {
            //Console.WriteLine("캡쳐하기");            
            Util.Capture.Tool.Make_Custom(_appController.Capture_Rect());
        }

        [DllImport("user32.dll", CharSet = CharSet.Auto)]
        private static extern IntPtr FindWindow(string lpClassName, string lpWindowName);
        [DllImport("user32.dll")] static extern bool PostMessage(IntPtr hWnd, uint Msg, IntPtr wParam, IntPtr lParam);
        const uint WM_KEYDOWN = 0x0100; // 키 누름
        const uint WM_KEYUP = 0x0101;   // 키 뗌
        const uint WM_CHAR = 0x0102;    // 문자 입력
        private void OnClick_Test4(object sender, EventArgs e)
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

        void Log_DetectResult(DEV.Tester0.Result_DetectIconImage __result)
        {
            TXT_Logger.Text = $"위치: x= {__result.pos.X}, y= {__result.pos.Y}" +
                $"\r\n사이즈: {__result.size.Width} X {__result.size.Height}" +
                $"\r\n유사도: {__result.similarity}";
        }

        void Processs_KeyDown(object sender, KeyEventArgs e)
        {
            if (Keys.Escape == e.KeyData)
            {
#if DEBUG
                Application.Exit();
                //MessageBox.Show("Escape 클릭");
#endif
            }
        }
    }
}
