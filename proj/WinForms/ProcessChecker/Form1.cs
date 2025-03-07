using System;
using System.Windows.Forms;

namespace ProcessChecker
{
    using System.Diagnostics;

    public partial class Form1 : Form
    {
        public Form1()
        {
            InitializeComponent();
        }

        public void OnClick_OK(object sender, EventArgs e)
        {
            if(string.IsNullOrEmpty(TBOX_PID.Text))
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

            TBOX_Result.Text = proc.ProcessName;
            {
                LBL_Result.Text = "결과 (Proc 이름)";
                Update_Handle(proc);
            }
            MessageBox.Show("앱을 찾았습니다.", "알림", MessageBoxButtons.OK, MessageBoxIcon.Information);
        }
        public void OnClick_PorcOK(object sender, EventArgs e)
        {
            if (string.IsNullOrEmpty(TBOX_PName.Text))
            {
                MessageBox.Show("PID를 입력하세요!", "경고", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }

            Process[] processes = Process.GetProcessesByName(TBOX_PName.Text);

            if (0 == processes.Length)
            {
                //Console.WriteLine("LORDNINE 을 실행하세요~~");
                MessageBox.Show($"해당 게임이 없습니다. Process Name({TBOX_PName.Text})를 확인하세요.", "에러", MessageBoxButtons.OK, MessageBoxIcon.Error);
                return;
            }

            TBOX_Result.Text = processes[0].Id.ToString();
            {
                LBL_Result.Text = "결과 (PID)";
                Update_Handle(processes[0]);
            }
            MessageBox.Show("앱을 찾았습니다.", "알림", MessageBoxButtons.OK, MessageBoxIcon.Information);
        }

        void Update_Handle(Process __process)
        {
            string text = $"Main: {__process.MainWindowHandle}";
            //if (nint.Zero != __process.Handle)
            //    text += $" ({__process.Handle})";

            TBOX_Handle.Text = text;
        }

        public void OnClick_Copy(object sender, EventArgs e)
        {
            Clipboard.SetText(TBOX_Result.Text);
            MessageBox.Show("클립보드에 복사하였습니다.", "알림", MessageBoxButtons.OK, MessageBoxIcon.Information);
        }
    }
}
