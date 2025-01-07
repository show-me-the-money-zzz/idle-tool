namespace IdleTool.Util
{
    using System.Runtime.InteropServices;

    internal class Importer
    {
        [DllImport("user32.dll", SetLastError = true)]
        static extern bool GetWindowRect(IntPtr __hwnd, out Common.Types.RECT __rect);

        public static bool Get_AppRect(IntPtr __hwnd, out Common.Types.RECT __rect) => GetWindowRect(__hwnd, out __rect);
    }
}
