namespace IdleTool.Util
{
    using Emgu.CV;
    using System.Drawing.Imaging;

    public class Finder
    {//https://tyen.tistory.com/74

        static readonly string PublicPath = "./public";
        //public
            static string LocalPath(string __path) => $"{PublicPath}/{__path}";

        public static string Open_FileDialog(string __initial_dir)
        {
            OpenFileDialog dialog = new OpenFileDialog();

            dialog.InitialDirectory = @"C:\";
            if (!string.IsNullOrEmpty(__initial_dir))
                dialog.InitialDirectory = __initial_dir;

            string file_str = string.Empty;

            if (DialogResult.Cancel == dialog.ShowDialog()) return string.Empty;
            else if(DialogResult.OK == dialog.ShowDialog())
                file_str = dialog.FileName;

#if DEBUG
            Console.WriteLine($"Util.Loader.Open_FileDialog({__initial_dir}): ({file_str})");
#endif

            return file_str;
        }

        public static Image? Load_LocalImage(string __path) => Bitmap.FromFile(LocalPath(__path));

        public static bool Save_LocalImage_PNG(System.Drawing.Image? __image, string __path) => Save_Image_PNG(__image, LocalPath(__path));
        public static bool Save_Image_PNG(System.Drawing.Image? __image, string __path)
        {
            if (null == __image) return false;

            string fullpath = $"{__path}.png";
            __image.Save(fullpath, ImageFormat.Png);

#if DEBUG
            Console.WriteLine($"캡처 이미지를 저장하였습니다(.png): {fullpath}");
#endif

            return true;
        }

        public static void Save_LocalBitmapImage_PNG(Bitmap __bitmap, string __path) => Save_BitmapImage_PNG(__bitmap, LocalPath(__path));
        public static void Save_BitmapImage_PNG(Bitmap __bitmap, string __path)
        {
            string fileName = $"{__path}.png";
            __bitmap.Save(fileName, ImageFormat.Png);

#if DEBUG
            Console.WriteLine($"캡처 이미지(Bitmap)를 저장하였습니다(.png): {fileName}");
#endif
        }
    }
}
