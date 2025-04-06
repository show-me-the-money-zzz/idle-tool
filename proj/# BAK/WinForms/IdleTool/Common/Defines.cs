namespace IdleTool.Common
{
    internal class Defines
    {
        public static readonly string AppName = "LORDNINE";//PID Process Name
        //LORDNINE.. ex) STOVE

        #region [예약 키워드]
        public enum Reserved_Keywords : int { NONE = -1,
            hp = 0, mp,
            potion,
            location,
        }
        //public static readonly string[] Reserved_Keywords_Text = { "hp", "mp", "물약", "지역", };
        public static string Reserved_Keywords_Text(Reserved_Keywords __keyword)
        {
            if (Reserved_Keywords.hp == __keyword) return "hp";
            else if (Reserved_Keywords.mp == __keyword) return "mp";
            else if (Reserved_Keywords.potion == __keyword) return "물약";
            else if (Reserved_Keywords.location == __keyword) return "지역";
            else return "";
        }
        #endregion
    }
}
