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
        ToolStripStatusLabel _LBL_Location = null;

        AsyncReactiveProperty<int?> HP { get; } = new AsyncReactiveProperty<int?>(default(int));
        AsyncReactiveProperty<int?> MP { get; } = new AsyncReactiveProperty<int?>(default(int));
        AsyncReactiveProperty<int?> POTION { get; } = new AsyncReactiveProperty<int?>(default(int));

        AsyncReactiveProperty<string?> LOCATION { get; } = new AsyncReactiveProperty<string?>("");

        public void Setup(App __app
            , ToolStripStatusLabel __lbl_hp, ToolStripStatusLabel __lbl_mp
            , ToolStripStatusLabel __lbl_potion
            , ToolStripStatusLabel __lbl_location
            )
        {
            _app = __app;

            _LBL_HP = __lbl_hp;
            _LBL_MP = __lbl_mp;
            _LBL_Potion = __lbl_potion;
            _LBL_Location = __lbl_location;

            Setup_Subscibe();

            Update_Stat().Forget();
        }

        void Setup_Subscibe()
        {
            HP.Subscribe(v => Update_StatText(_LBL_HP, "HP", v));
            MP.Subscribe(v => Update_StatText(_LBL_MP, "MP", v));

            POTION.Subscribe(v => Update_StatText(_LBL_Potion, "물약", v));

            LOCATION.Subscribe(v => {
                string text = "위치: ";
                text += string.IsNullOrEmpty(v) ? "" : v;
                _LBL_Location.Text = text;
            });
        }

        void Update_StatText(ToolStripStatusLabel __lable, string __kind, int? __value)
        {
            string text = $"{__kind} ";

            if (null == __value) text += "(읽기실패)";
            else text += $"{__value:#,###}";

            __lable.Text = text;
        }

        //public void Set_Potion(int __potion) => POTION.Value = __potion;

        void Parse_Number(AsyncReactiveProperty<int?> __rp, string __var, bool __isHPMP)
        {
            if (string.IsNullOrEmpty(__var))
            {
                __rp.Value = null;
                return;
            }

            __var = __var.Replace(",", "");
            __var = __var.Replace(".", "");//,를 .로 인식한 경우 대비

            if (__isHPMP)
                __var = __var.Split("/")[0];

            int parsevar = 0;

            if (int.TryParse(__var, out parsevar))
            {
                __rp.Value = parsevar;
            }
            else __rp.Value = null;
        }

        async UniTask Update_Stat()
        {
            double TICK = 1.0d;
            //{ TICK = 0.05d; }
            { TICK = 0.001d; }

            while (true)
            {
                await Task.Delay(TimeSpan.FromSeconds(TICK));
                //Console.WriteLine($"Tick: {DateTime.Now}");

                var bmp_app = Util.Capture.Tool.NewMake(_app);

                string keyword = "";
                Rectangle textRegion = new Rectangle();

                //POTION
                keyword = Common.Defines.Reserved_Keywords_Text(Common.Defines.Reserved_Keywords.potion);
                if (Common.Stores.Instance.List_TextArea.ContainsKey(keyword))
                {
                    textRegion = Common.Stores.Instance.List_TextArea[keyword];
                    var potion = await Util.OCR.ReadText_CropRegion(bmp_app, textRegion, __isNumber: true
                        //, __name: keyword
                        );
                    Parse_Number(POTION, potion, false);
#if DEBUG
                    //Console.WriteLine($"potion: {potion}");
#endif
                }

                ////HP
                keyword = Common.Defines.Reserved_Keywords_Text(Common.Defines.Reserved_Keywords.hp);
                if (Common.Stores.Instance.List_TextArea.ContainsKey(keyword))
                {
                    textRegion = Common.Stores.Instance.List_TextArea[keyword];
                    var hp = await Util.OCR.ReadText_CropRegion(bmp_app, textRegion, __isNumber: true
                        //, __name: keyword
                        );
                    Parse_Number(HP, hp, true);
#if DEBUG
                    //Console.WriteLine($"hp: {hp}");
#endif
                }

                ////MP
                keyword = Common.Defines.Reserved_Keywords_Text(Common.Defines.Reserved_Keywords.mp);
                if (Common.Stores.Instance.List_TextArea.ContainsKey(keyword))
                {
                    textRegion = Common.Stores.Instance.List_TextArea[keyword];
                    var mp = await Util.OCR.ReadText_CropRegion(bmp_app, textRegion, __isNumber: true
                        //, __name: keyword
                        );
                    Parse_Number(MP, mp, true);
#if DEBUG
                    //Console.WriteLine($"mp: {mp}");
#endif
                }

                ////Location
                keyword = Common.Defines.Reserved_Keywords_Text(Common.Defines.Reserved_Keywords.location);
                if (Common.Stores.Instance.List_TextArea.ContainsKey(keyword))
                {
                    textRegion = Common.Stores.Instance.List_TextArea[keyword];
                    LOCATION.Value = await Util.OCR.ReadText_CropRegion(bmp_app, textRegion, __isNumber: false
                        //, __name: keyword
                        );
#if DEBUG
                    //Console.WriteLine($"지역: {LOCATION.Value}");
#endif
                }
            }
        }
    }
}
