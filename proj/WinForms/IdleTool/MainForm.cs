namespace IdleTool
{
    public partial class MainForm : Form
    {
        int _count = 0;

        public MainForm()
        {
            InitializeComponent();
            KeyPreview = true;
        }

        private void OnClick_Test1(object sender, EventArgs e)
        {
            _count += 1;
            TXT_Logger.Text = $"클릭 {_count}\r\n테스트";
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
