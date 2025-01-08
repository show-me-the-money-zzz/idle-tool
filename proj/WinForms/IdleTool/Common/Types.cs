namespace IdleTool.Common
{
    //using System.Numerics;
    using System.Runtime.InteropServices;

    public class Types
    {
        [StructLayout(LayoutKind.Sequential)]
        public struct RECT
        {
            public int Left;
            public int Top;
            public int Right;
            public int Bottom;

            public int Width => Right - Left;
            public int Height => Bottom - Top;

            public Size Get_Size() => new Size(Width, Height);

            public bool IsValid => (0 < Width && 0 < Height);
        }
    }
}
