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
            { Test_App(); }//DEV TEST
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

            DEV.Tester0.Detect_IconImage_byLocal(_appController);
        }

        void Processs_KeyDown(object sender, KeyEventArgs e)
        {
            if(Keys.Escape == e.KeyData)
            {
#if DEBUG
                Application.Exit();
                MessageBox.Show("Escape 클릭");
#endif
            }
        }
    }
}
