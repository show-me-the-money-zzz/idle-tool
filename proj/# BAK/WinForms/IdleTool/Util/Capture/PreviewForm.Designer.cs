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

                int formHeight = Math.Min(__captured.Height + 150, Screen.PrimaryScreen.WorkingArea.Height);
                int formWidth = Math.Min(__captured.Width, Screen.PrimaryScreen.WorkingArea.Width);

                this.ClientSize = new Size(formWidth, formHeight);
                this.MinimumSize = new Size(500, 150);

                this.KeyPreview = true;
                this.KeyDown += Processs_KeyDown;
            }

            FlowLayoutPanel pane_TopButtons = null;
            {//상단 버튼 모음
                // 🔹 "저장" 버튼
                _btn_Save = new Button { Text = "저장", AutoSize = true, Width = 80, Margin = new Padding(3) };
                _btn_Save.Click += OnClick_Save;

                // 🔹 "취소" 버튼
                _btn_Cancel = new Button { Text = "다시 캡쳐", AutoSize = true, Width = 80, Margin = new Padding(3) };
                _btn_Cancel.Click += OnClick_Retry;

                // 🔹 버튼을 가로 정렬하는 패널 (상단에 배치)
                pane_TopButtons = new FlowLayoutPanel {
                    FlowDirection = FlowDirection.LeftToRight,
                    Dock = DockStyle.Fill,
                    AutoSize = true,
                    Padding = new Padding(2)
                };
                pane_TopButtons.Controls.Add(_btn_Save);
                pane_TopButtons.Controls.Add(_btn_Cancel);
            }

            TableLayoutPanel inputFieldsPanel = null;
            {//RECT Panel
                const int Line_Inputs = 1; // 행 개수
                string[] LabelText = { "좌 (左)", "상 (上)", "우 (右)", "하 (下)" };

                // 🔹 입력 필드 영역을 위한 `TableLayoutPanel`
                inputFieldsPanel = new TableLayoutPanel {
                    ColumnCount = 9,
                    RowCount = Line_Inputs,
                    Dock = DockStyle.Fill,
                    AutoSize = true,
                    Padding = new Padding(2),
                    Margin = new Padding(2),
                    CellBorderStyle = TableLayoutPanelCellBorderStyle.Outset,
                };

                int colindex = 0;
                for (int i = 0; i < Line_Inputs; i++)
                {
                    for (int j = 0; j < 4; j++) // 4개의 입력 필드
                    {
                        Label lbl = new Label {
                            Text = LabelText[j],
                            AutoSize = true,
                            TextAlign = ContentAlignment.MiddleRight,
                            Anchor = AnchorStyles.Right,
                            Margin = new Padding(2)
                        };

                        _tbox_list_rect[j] = new TextBox {
                            Width = 50, // ❗ 입력칸 폭을 줄여서 불필요한 공간 제거
                            Anchor = AnchorStyles.Left,
                            Margin = new Padding(2)
                        };

                        inputFieldsPanel.Controls.Add(lbl, colindex++, i);
                        inputFieldsPanel.Controls.Add(_tbox_list_rect[j], colindex++, i);
                    }
                }

                // 🔹 "적용" 버튼 (입력 필드 옆에 위치)
                Button btn_Update = new Button {
                    Text = "적용",
                    AutoSize = true,
                    Width = 60, // ❗ 버튼 폭을 줄여서 불필요한 공간 최소화
                    Margin = new Padding(2)
                };
                btn_Update.Click += OnClick_Update_Rect;
                inputFieldsPanel.Controls.Add(btn_Update, colindex, 0);
            }

            FlowLayoutPanel pane_SubInfo = null;
            {//이름 등 추가 정보
                _txtbox_Key = new TextBox {
                    Width = 150, // ❗ 입력칸 폭을 줄여서 불필요한 공간 제거
                    Anchor = AnchorStyles.Left,
                    Margin = new Padding(2)
                };

                pane_SubInfo = new FlowLayoutPanel {
                    FlowDirection = FlowDirection.LeftToRight,
                    Dock = DockStyle.Fill,
                    AutoSize = true,
                    Padding = new Padding(2)
                };

                pane_SubInfo.Controls.Add(_txtbox_Key);
            }

            // 🔹 `PictureBox` 설정 (이미지 표시, 아래 배치)
            _picbox = new PictureBox {
                Image = __captured,
                SizeMode = PictureBoxSizeMode.Zoom,
                Dock = DockStyle.Fill,
                BorderStyle = BorderStyle.FixedSingle
            };

            // 🔹 전체 레이아웃을 관리하는 `TableLayoutPanel`
            TableLayoutPanel mainLayout = new TableLayoutPanel {
                Dock = DockStyle.Fill,
                ColumnCount = 1,
                RowCount = 3
            };

            // 🔹 행 높이 설정 (입력 필드 영역 높이 줄이기)
            mainLayout.RowStyles.Add(new RowStyle(SizeType.Absolute, 36));  // 버튼 영역 (줄임)
            mainLayout.RowStyles.Add(new RowStyle(SizeType.Absolute, 36));  // 입력 필드 영역 (최소화)
            mainLayout.RowStyles.Add(new RowStyle(SizeType.Absolute, 36));  // 입력 필드 영역 (최소화)
            mainLayout.RowStyles.Add(new RowStyle(SizeType.Percent, 100));  // 이미지 영역 (남은 공간)

            {// 🔹 컨트롤 추가
                int row = 0;
                mainLayout.Controls.Add(pane_TopButtons, 0, row++); // 1행 (버튼)
                mainLayout.Controls.Add(inputFieldsPanel, 0, row++); // 2행 (입력 필드)
                mainLayout.Controls.Add(pane_SubInfo, 0, row++); // 3행
                mainLayout.Controls.Add(_picbox, 0, row++);          // 4행 (이미지)
            }

            // 🔹 폼에 전체 레이아웃 추가
            this.Controls.Add(mainLayout);
        }

        #region [Controls]
        PictureBox _picbox;

        Button _btn_Save;
        Button _btn_Cancel;

        TextBox _txtbox_Key = null;

        TextBox[] _tbox_list_rect = new TextBox[4];
        #endregion
    }
}
