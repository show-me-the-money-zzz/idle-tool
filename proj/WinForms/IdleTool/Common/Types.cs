namespace IdleTool.Common
{
    using System.Runtime.InteropServices;

    internal class Types
    {
        [StructLayout(LayoutKind.Sequential)]
        public struct RECT
        {
            public int Left;
            public int Top;
            public int Right;
            public int Bottom;
        }
    }
}
