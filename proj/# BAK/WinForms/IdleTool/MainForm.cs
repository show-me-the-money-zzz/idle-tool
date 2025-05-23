namespace IdleTool
{
    //using IdleTool.Controller;
    //using System.Diagnostics;
    //using System.Drawing;
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
            Util.Finder.Read_JsonData_Textarea();
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

        [DllImport("user32.dll")] static extern bool PostMessage(IntPtr hWnd, uint Msg, IntPtr wParam, IntPtr lParam);
        private void OnClick_Test4(object sender, EventArgs e)
        {
            InputTest();
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
