using System.Diagnostics;

namespace ProcessChecker
{
    public partial class Form1 : Form
    {
        public Form1()
        {
            InitializeComponent();
        }

        public void OnClick_Check_PID(object sender, EventArgs e)
        {
            if (string.IsNullOrEmpty(TBOX_PID.Text))
            {
                MessageBox.Show("PID를 입력하세요!", "경고", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }

            var PID = int.Parse(TBOX_PID.Text);

            var proc = Process.GetProcessById(PID);
            if (null == proc)
            {
                MessageBox.Show($"해당 게임이 없습니다. PID({PID})를 확인하세요.", "에러", MessageBoxButtons.OK, MessageBoxIcon.Error);
                return;
            }

            TBOX_RESULT.Text = proc.ProcessName;
            {
                LBL_RESULT.Text = "결과 (P NAME)";
                Update_Handle(proc);
            }
            MessageBox.Show("앱을 찾았습니다.", "알림", MessageBoxButtons.OK, MessageBoxIcon.Information);
        }
        public void OnClick_Check_PName(object sender, EventArgs e)
        {
            if (string.IsNullOrEmpty(TBOX_PNAME.Text))
            {
                MessageBox.Show("PID를 입력하세요!", "경고", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }

            Process[] processes = Process.GetProcessesByName(TBOX_PNAME.Text);

            if (0 == processes.Length)
            {
                //Console.WriteLine("LORDNINE 을 실행하세요~~");
                MessageBox.Show($"해당 게임이 없습니다. Process Name({TBOX_PNAME.Text})를 확인하세요.", "에러", MessageBoxButtons.OK, MessageBoxIcon.Error);
                return;
            }

            TBOX_RESULT.Text = processes[0].Id.ToString();
            {
                LBL_RESULT.Text = "결과 (PID)";
                Update_Handle(processes[0]);
            }
            MessageBox.Show("앱을 찾았습니다.", "알림", MessageBoxButtons.OK, MessageBoxIcon.Information);
        }

        void Update_Handle(Process __process)
        {
            string text = $"Main: ";
            if (nint.Zero == __process.MainWindowHandle) text += "0";
            else text += $"{__process.MainWindowHandle}";
            //Console.WriteLine($"MainWindowHandle= {__process.MainWindowHandle}");

            try
            {
                if (nint.Zero != __process.Handle)
                {
                    text += $" ({__process.Handle})";
                    //Console.WriteLine($"Handle= {__process.Handle}");
                }
            }
            catch
            {
            }

            TBOX_HANDLE.Text = text;
        }

        public void OnClick_Copy(object sender, EventArgs e)
        {
            Clipboard.SetText(TBOX_RESULT.Text);
            MessageBox.Show("클립보드에 복사하였습니다.", "알림", MessageBoxButtons.OK, MessageBoxIcon.Information);
        }

        public void OnClick_Reset(object sender, EventArgs e)
        {
            TBOX_PID.Text = "";
            TBOX_PNAME.Text = "";

            TBOX_RESULT.Text = "";
            TBOX_HANDLE.Text = "";
        }
    }
}
