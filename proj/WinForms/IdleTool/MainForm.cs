using Emgu.CV.CvEnum;
using System.Windows.Forms;

namespace IdleTool
{
    public partial class MainForm : Form
    {
        Controller.App _appController = null;

        int _count = 0;

        public MainForm(Controller.App __app)
        {
            InitializeComponent();

            KeyPreview = true;//키 입력 안 먹을 때
            //https://free-sounds.tistory.com/39

            _appController = __app;
            //{ Test_App(); }//DEV TEST

            {
                //foreach (ToolStripItem item in statusStrip.Items)
                //    Console.WriteLine($"아이템: {item.Text}, 타입: {item.GetType()}");
                //statusStrip.SizingGrip = true;
                //statusStrip.Refresh();

                statusLabel_State.Text = "게임 찾기 성공!!";

                //statusLabel_HP.Text = $"HP ({150:#,###}/{7650:#,###})";
                statusLabel_HP.Text = $"HP {7650:#,###}";
                statusLabel_MP.Text = $"MP {1500:#,###}";
                statusLabel_Potion.Text = $"HP {1118:#,###}";
            }
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
            _count += 1;
            TXT_Logger.Text = $"클릭 {_count}\r\n테스트";

            Log_DetectResult(DEV.Tester0.Detect_IconImage_byLocal(_appController, "icon-worldmap"));
        }
        private void OnClick_Test2(object sender, EventArgs e)
        {
            Log_DetectResult(DEV.Tester0.Detect_IconImage_byLocal(_appController, "icon-inventory"));
        }
        private void OnClick_Test3(object sender, EventArgs e)
        {
            //DEV.FormText.Find_TextEdit();

            Rectangle textRegion = new Rectangle(538, 1043, 86, 22);//potion
            textRegion = new Rectangle(590, 1050, 56, 20);//ZZUNY+중간
            {//HP
                textRegion = new Rectangle(62, 54, 210, 25);//ZZUNY+중간

                {//MP
                    textRegion = new Rectangle(62, 78, 210, 25);//ZZUNY+중간
                }
            }
            Util.OCR.Read_Text(_appController, textRegion, __isNumber: true, __filename: "potion");
        }
        private void OnClick_Test4(object sender, EventArgs e)
        {
            Rectangle textRegion = new Rectangle(220, 200, 110, 40);//현재 위치 텍스트
            textRegion = new Rectangle(200, 186, 100, 30);
            Util.OCR.Read_Text(_appController, textRegion, __isNumber: false, __filename: "maplocation");
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
