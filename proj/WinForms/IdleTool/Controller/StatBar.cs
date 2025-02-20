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
            Rectangle textRegion_Potion = new Rectangle(550, 1045, 60, 20);//potion
            //{ textRegion_Potion = new Rectangle(590, 1050, 56, 20); }//ZZUNY+중간
            Rectangle textRegion_HP = new Rectangle(64, 58, 306, 26);
            //{ textRegion_HP = new Rectangle(60, 56, 240, 22); }//ZZUNY+중간
            Rectangle textRegion_MP = new Rectangle(64, 84, 306, 26);
            //{ textRegion_MP = new Rectangle(60, 80, 240, 22); }//ZZUNY+중간

            Rectangle textRegion_Location = new Rectangle(222, 206, 180, 26);
            //{ textRegion_Location = new Rectangle(200, 190, 160, 22); }//ZZUNY+중간

            double TICK = 1.0d;
            //{ TICK = 0.05d; }
            { TICK = 0.001d; }

            /*const*/ string[] Names = {
                "",//potion
                "",//hp
                "",//mp
                "",//location
            };

            while (true)
            {
                await Task.Delay(TimeSpan.FromSeconds(TICK));
                //Console.WriteLine($"Tick: {DateTime.Now}");

                var bmp_app = Util.CaptureTool.NewMake(_app);

                ////POTION
                var potion = Util.OCR.ReadText_CropRegion(bmp_app, textRegion_Potion, __isNumber: true, __name: Names[0]);
                Parse_Number(POTION, potion, false);

                ////HP
                var hp = Util.OCR.ReadText_CropRegion(bmp_app, textRegion_HP, __isNumber: true, __name: Names[1]);
                Parse_Number(HP, hp, true);

                ////MP
                var mp = Util.OCR.ReadText_CropRegion(bmp_app, textRegion_MP, __isNumber: true, __name: Names[2]);
                Parse_Number(MP, mp, true);

                ////Location
                LOCATION.Value = Util.OCR.ReadText_CropRegion(bmp_app, textRegion_Location, __isNumber: false, __name: Names[3]);
            }
        }
    }
}
