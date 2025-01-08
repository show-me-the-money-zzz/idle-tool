namespace IdleTool.Util
{
    public class Finder
    {//https://tyen.tistory.com/74

        static readonly string PublicPath = "./public";

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
    }
}
