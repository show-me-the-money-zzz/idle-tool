namespace IdleTool.Util
{
    using System.Runtime.InteropServices;

    internal class Importer
    {
        [DllImport("user32.dll", SetLastError = true)]
        static extern bool GetWindowRect(IntPtr __hwnd, out Common.Types.RECT __rect);

        //public static bool Get_AppRect(IntPtr __hwnd, out Common.Types.RECT __rect) => GetWindowRect(__hwnd, out __rect);
        public static Common.Types.RECT Get_AppRect(IntPtr __hwnd)
        {
            Common.Types.RECT ret = new Common.Types.RECT();
            GetWindowRect(__hwnd, out ret);
            return ret;
        }
    }
}
