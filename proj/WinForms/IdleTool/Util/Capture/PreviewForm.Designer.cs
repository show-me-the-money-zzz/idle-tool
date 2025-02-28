namespace IdleTool.Util.Capture
{
    using System.Windows.Forms;

    partial class PreviewForm
    {
        System.ComponentModel.IContainer components = null;

        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        void InitializeComponent(Bitmap __captured)
        {
            {// 🔹 폼 기본 설정
                this.Text = "미리보기";
                this.StartPosition = FormStartPosition.CenterScreen;
                this.FormBorderStyle = FormBorderStyle.FixedDialog;
                this.MaximizeBox = false;
                this.MinimizeBox = false;

                // ❗ `ClientSize`를 설정하여 버튼과 이미지 크기를 고려
                int formHeight = Math.Min(__captured.Height + 80, Screen.PrimaryScreen.WorkingArea.Height);
                int formWidth = Math.Min(__captured.Width, Screen.PrimaryScreen.WorkingArea.Width);

                this.ClientSize = new Size(formWidth, formHeight);
                this.MinimumSize = new Size(300, 200); // 버튼이 항상 보이도록 최소 크기 지정
            }

            // 🔹 저장 버튼 설정
            _btn_Save = new Button {
                Text = "저장",
                AutoSize = true,
                Width = 80, // 버튼 크기 지정
                Margin = new Padding(5)
            };
            _btn_Save.Click += OnClick_Save;

            // 🔹 취소 버튼 설정
            _btn_Cancel = new Button {
                Text = "다시",
                AutoSize = true,
                Width = 80,
                Margin = new Padding(5)
            };
            _btn_Cancel.Click += OnClick_Retry;

            // 🔹 FlowLayoutPanel 설정 (버튼을 가로 정렬, 위에 배치)
            _pane_TopButtons = new FlowLayoutPanel {
                FlowDirection = FlowDirection.LeftToRight, // 가로 정렬
                AutoSize = true,
                Height = 50,
                Padding = new Padding(10),
                Dock = DockStyle.Fill, // TableLayoutPanel 내에서만 Fill
                Anchor = AnchorStyles.Left | AnchorStyles.Right
            };

            // 🔹 버튼을 패널에 추가
            _pane_TopButtons.Controls.Add(_btn_Save);
            _pane_TopButtons.Controls.Add(_btn_Cancel);

            // 🔹 PictureBox 설정 (이미지 표시, 아래 배치)
            _picbox = new PictureBox {
                Image = __captured,
                SizeMode = PictureBoxSizeMode.Zoom, // 폼 크기에 맞게 자동 조정
                Dock = DockStyle.Fill // 🔹 TableLayoutPanel 내에서만 Fill 설정
            };

            // 🔹 TableLayoutPanel 설정 (버튼과 이미지 영역을 나눔)
            TableLayoutPanel mainLayout = new TableLayoutPanel {
                Dock = DockStyle.Fill,
                ColumnCount = 1,
                RowCount = 2
            };

            // 🔹 행 높이 설정 (버튼 영역: 60px 고정, 이미지 영역: 남은 공간)
            mainLayout.RowStyles.Add(new RowStyle(SizeType.Absolute, 60)); // 버튼 영역
            mainLayout.RowStyles.Add(new RowStyle(SizeType.Percent, 100)); // 이미지 영역 (남은 공간 차지)

            // 🔹 컨트롤 추가 (순서 중요)
            mainLayout.Controls.Add(_pane_TopButtons, 0, 0); // 첫 번째 행 (버튼)
            mainLayout.Controls.Add(_picbox, 0, 1); // 두 번째 행 (이미지)

            // 🔹 폼에 TableLayoutPanel 추가
            this.Controls.Add(mainLayout);
        }

        #region [Controls]
        PictureBox _picbox;

        FlowLayoutPanel _pane_TopButtons;
        Button _btn_Save;
        Button _btn_Cancel;
        #endregion
    }
}
