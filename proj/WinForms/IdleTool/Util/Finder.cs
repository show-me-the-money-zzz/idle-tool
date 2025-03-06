namespace IdleTool.Util
{
    using System.IO;
    using System.Drawing.Imaging;
    using Newtonsoft.Json.Linq;
    using Newtonsoft.Json;

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

        static string GetPath_JsonData(string __filename) => @$"{LocalPath("data")}/{__filename}.json";
        static readonly string Json_Name_Textarea = "textarea";

        static JObject Read_JsonData(string __filename)
        {
#if DEBUG
            //Console.WriteLine($"Read_JsonData({__filename}): {path}");
#endif
            using (StreamReader file = File.OpenText(GetPath_JsonData(__filename)))
            {
                using (JsonTextReader reader = new JsonTextReader(file))
                {
                    JObject json = (JObject)JToken.ReadFrom(reader);
#if DEBUG
                    //Console.WriteLine(json.ToString());
#endif
                    return json;
                }
            }
        }

        /*
         * (참고) Newtonsoft.Json을 사용 JSON 파일을 저장.md
         */
        static void Write_JsonData(string __filename, string __strjson)
        {
            //using (StreamWriter file = File.CreateText(GetPath_JsonData(__filename)))
            //{
            //    using (JsonTextWriter writer = new JsonTextWriter(file))
            //    {
            //        __json.WriteTo(writer);
            //    }
            //}

            File.WriteAllText(GetPath_JsonData(__filename), __strjson);
        }        

        public static int Read_JsonData_Textarea()
        {
            var json = Read_JsonData(Json_Name_Textarea);
#if DEBUG
            Console.WriteLine($"Read_JsonData_Textarea [{json.Count}] {json.ToString()}");
#endif
            foreach (var item in json)
            {
                string key = item.Key;
                var val = (item.Value).ToString().Split(",");
                {
                    var rectangle = new Rectangle();
                    {
                        rectangle.X = int.Parse(val[0]);
                        rectangle.Y = int.Parse(val[1]);
                        rectangle.Width = int.Parse(val[2]);
                        rectangle.Height = int.Parse(val[3]);
                    }
                    Common.Stores.Instance.List_TextArea.Add(key, rectangle);
                }
            };
#if DEBUG
            //int index = 0;
            //foreach (var item in Common.Stores.Instance.List_TextArea)
            //    Console.WriteLine($"[{index++}] {item}");
#endif
            return Common.Stores.Instance.List_TextArea.Count;
        }

        public static void Write_JsonData_Textarea()
        {
            string strjson = JsonConvert.SerializeObject(Common.Stores.Instance.List_TextArea, Formatting.Indented);
#if DEBUG
            //Console.WriteLine($"Write_JsonData_Textarea({strjson}):");
#endif
            Write_JsonData(Json_Name_Textarea, strjson);
        }
    }
}
