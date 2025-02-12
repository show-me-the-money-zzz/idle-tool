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

            Update_HP().Forget();
            Update_MP().Forget();
            Update_Potion().Forget();
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

        async UniTask Update_HP()
        {
            Rectangle textRegion = new Rectangle(64, 58, 306, 26);

            while (true)
            {
                await Task.Delay(TimeSpan.FromSeconds(1.0d));
                //Console.WriteLine($"Tick: {DateTime.Now}");

                var hp = Util.OCR.Read_Text(_app, textRegion, __isNumber: true
                    //, __filename: "hp"
                    );
                {
                    hp = hp.Split("/")[0];

                    int outvalue = 0;
                    if (int.TryParse(hp, out outvalue))
                    {
                        HP.Value = outvalue;
                    }
                    else
                    {
                        _LBL_HP.Text = "HP (실패)";
                    }
                }
            }
        }
        async UniTask Update_MP()
        {
            Rectangle textRegion = new Rectangle(64, 84, 306, 26);

            while (true)
            {
                await Task.Delay(TimeSpan.FromSeconds(1.0d));
                //Console.WriteLine($"Tick: {DateTime.Now}");

                var mp = Util.OCR.Read_Text(_app, textRegion, __isNumber: true
                    //, __filename: "mp"
                    );
                {
                    mp = mp.Split("/")[0];

                    int outvalue = 0;
                    if (int.TryParse(mp, out outvalue))
                    {
                        MP.Value = outvalue;
                    }
                    else
                    {
                        _LBL_MP.Text = "MP (실패)";
                    }
                }
            }
        }

        async UniTask Update_Potion()
        {
            Rectangle textRegion = new Rectangle(550, 1045, 60, 20);//potion
            //textRegion = new Rectangle(590, 1050, 56, 20);//ZZUNY+중간

            while (true)
            {
                await Task.Delay(TimeSpan.FromSeconds(1.0d));
                //Console.WriteLine($"Tick: {DateTime.Now}");

                var potion = Util.OCR.Read_Text(_app, textRegion, __isNumber: true
                    //, __filename: "potion"
                    );
                {
                    int outvalue = 0;
                    if (int.TryParse(potion, out outvalue))
                    {
                        POTION.Value = outvalue;
                    }
                    else
                    {
                        _LBL_Potion.Text = "물약 (실패)";
                    }
                }
            }
        }
    }
}
