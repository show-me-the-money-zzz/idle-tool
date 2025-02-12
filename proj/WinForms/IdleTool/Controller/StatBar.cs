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

        AsyncReactiveProperty<int?> HP { get; } = new AsyncReactiveProperty<int?>(default(int));
        AsyncReactiveProperty<int?> MP { get; } = new AsyncReactiveProperty<int?>(default(int));
        AsyncReactiveProperty<int?> POTION { get; } = new AsyncReactiveProperty<int?>(default(int));

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
                Update_StatText(_LBL_HP, "HP", v);
            });
            MP.Subscribe(v => {
                Update_StatText(_LBL_MP, "MP", v);
            });

            POTION.Subscribe(v => {
                Update_StatText(_LBL_Potion, "물약", v);
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
                if (string.IsNullOrEmpty(potion)) POTION.Value = null;
                else POTION.Value = Parse_Number(potion, false);

                //HP
                var hp = Util.OCR.Read_Text_byCaptured(bmp_app, textRegion_HP, __isNumber: true
                    //, __filename: "hp"
                    );
                if (string.IsNullOrEmpty(hp)) HP.Value = null;
                else HP.Value = Parse_Number(hp, true);

                //MP
                var mp = Util.OCR.Read_Text_byCaptured(bmp_app, textRegion_MP, __isNumber: true
                    //, __filename: "mp"
                    );
                if (string.IsNullOrEmpty(mp)) MP.Value = null;
                else MP.Value = Parse_Number(mp, true);
            }
        }
    }
}
