namespace IdleTool.Controller
{
    using Cysharp.Threading.Tasks;
    using Cysharp.Threading.Tasks.Linq;

    internal class StatBar
    {
        App _app = null;

        ToolStripStatusLabel _LBL_Potion = null;

        AsyncReactiveProperty<int> POTION { get; } = new AsyncReactiveProperty<int>(0);

        public void Setup(App __app, ToolStripStatusLabel __lbl_potion)
        {
            _app = __app;
            _LBL_Potion = __lbl_potion;

            POTION.Subscribe(v => {
                _LBL_Potion.Text = $"물약 {v:#,###}";
            });

            Update_Potion().Forget();
        }

        public void Set_Potion(int __potion) => POTION.Value = __potion;

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
