namespace IdleTool.Controller
{
    using Cysharp.Threading.Tasks;
    using Cysharp.Threading.Tasks.Linq;

    internal class StatBar
    {
        App _app = null;

        ToolStripStatusLabel _LBL_HP = null;
        ToolStripStatusLabel _LBL_MP = null;
        ToolStripStatusLabel _LBL_Potion = null;

        AsyncReactiveProperty<int> HP { get; } = new AsyncReactiveProperty<int>(0);
        AsyncReactiveProperty<int> MP { get; } = new AsyncReactiveProperty<int>(0);
        AsyncReactiveProperty<int> POTION { get; } = new AsyncReactiveProperty<int>(0);

        public void Setup(App __app
            , ToolStripStatusLabel __lbl_hp, ToolStripStatusLabel __lbl_mp
            , ToolStripStatusLabel __lbl_potion
            )
        {
            _app = __app;

            _LBL_HP = __lbl_hp;
            _LBL_MP = __lbl_mp;
            _LBL_Potion = __lbl_potion;

            Setup_Subscibe();

            Update_Stat().Forget();
        }

        void Setup_Subscibe()
        {
            HP.Subscribe(v => {
                _LBL_HP.Text = $"HP {v:#,###}";
            });
            MP.Subscribe(v => {
                _LBL_MP.Text = $"MP {v:#,###}";
            });

            POTION.Subscribe(v => {
                _LBL_Potion.Text = $"물약 {v:#,###}";
            });
        }

        //public void Set_Potion(int __potion) => POTION.Value = __potion;

        int? Parse_Number(string __var, bool __isHPMP = false)
        {
            __var = __var.Replace(",", "");

            if(__isHPMP)
                __var = __var.Split("/")[0];

            int ret = 0;
            if (int.TryParse(__var, out ret))
                return ret;
            else
                return null;
        }

        async UniTask Update_Stat()
        {
            Rectangle textRegion_Potion = new Rectangle(550, 1045, 60, 20);//potion
            //textRegion = new Rectangle(590, 1050, 56, 20);//ZZUNY+중간

            Rectangle textRegion_HP = new Rectangle(64, 58, 306, 26);
            Rectangle textRegion_MP = new Rectangle(64, 84, 306, 26);

            while (true)
            {
                await Task.Delay(TimeSpan.FromSeconds(1.0d));
                //Console.WriteLine($"Tick: {DateTime.Now}");

                var bmp_app = Util.CaptureTool.NewMake(_app);

                //POTION
                var potion = Util.OCR.Read_Text_byCaptured(bmp_app, textRegion_Potion, __isNumber: true
                    //, __filename: "potion"
                    );

                var num_potion = Parse_Number(potion, false);
                if (null == num_potion) _LBL_Potion.Text = "물약 (실패)";
                else
                {
                    POTION.Value = num_potion ?? 0;
                }

                //HP
                var hp = Util.OCR.Read_Text_byCaptured(bmp_app, textRegion_HP, __isNumber: true
                    //, __filename: "hp"
                    );

                var num_hp = Parse_Number(hp, true);
                if (null == num_hp) _LBL_HP.Text = "HP (실패)";
                else
                {
                    HP.Value = num_hp ?? 0;
                }

                //MP
                var mp = Util.OCR.Read_Text_byCaptured(bmp_app, textRegion_MP, __isNumber: true
                    //, __filename: "mp"
                    );

                var num_mp = Parse_Number(mp, true);
                if (null == num_mp) _LBL_MP.Text = "MP (실패)";
                else
                {
                    MP.Value = num_mp ?? 0;
                }
            }
        }
    }
}
