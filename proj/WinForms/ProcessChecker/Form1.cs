using System;
using System.Windows.Forms;

namespace ProcessChecker
{
    using System.Diagnostics;
    using System.Security.Cryptography;

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

            TBOX_PName.Text = proc.ProcessName;
            MessageBox.Show("앱을 찾았습니다.", "알림", MessageBoxButtons.OK, MessageBoxIcon.Information);
        }
        public void OnClick_PorcOK(object sender, EventArgs e)
        {
            if (string.IsNullOrEmpty(TBOX_PID.Text))
            {
                MessageBox.Show("PID를 입력하세요!", "경고", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }

            Process[] processes = Process.GetProcessesByName(TBOX_PID.Text);

            if (0 == processes.Length)
            {
                //Console.WriteLine("LORDNINE 을 실행하세요~~");
                MessageBox.Show($"해당 게임이 없습니다. Process Name({TBOX_PID.Text})를 확인하세요.", "에러", MessageBoxButtons.OK, MessageBoxIcon.Error);
                return;
            }

            TBOX_PName.Text = processes[0].Id.ToString();
            MessageBox.Show("앱을 찾았습니다.", "알림", MessageBoxButtons.OK, MessageBoxIcon.Information);
        }

        public void OnClick_Copy(object sender, EventArgs e)
        {
            Clipboard.SetText(TBOX_PName.Text);
            MessageBox.Show("클립보드에 복사하였습니다.", "알림", MessageBoxButtons.OK, MessageBoxIcon.Information);
        }
    }
}
