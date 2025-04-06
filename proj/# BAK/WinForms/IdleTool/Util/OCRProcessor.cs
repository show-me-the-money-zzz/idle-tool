namespace IdleTool.Util
{
    using Tesseract;

    internal class OCRProcessor : IDisposable
    {//TesseractEngine 최적화 및 리소스 관리.md 참조 (by ChatGPT)
        private static TesseractEngine engine = null;
        private static readonly object lockObj = new object();
        private bool isDisposed = false;

        const string Path_Tessdata = @"./tessdata";
        string Get_Langs()
        {
            var ret = "eng+kor+kor_vert";
            //{
            //    Langs = "kor";
            //    Langs = "kor_vert";
            //    Langs = "kor+kor_vert";
            //}
            return ret;
        }
        public OCRProcessor()
        {
            // 1. 싱글톤 방식으로 엔진 생성 (스레드 안전)
            if (engine == null)
            {
                lock (lockObj)
                {
                    if (engine == null) // 이중 체크 (스레드 안정성 보장)
                    {
                        engine = new TesseractEngine(Path_Tessdata, "eng+kor+kor_vert", EngineMode.Default);
                    }
                }
            }
        }

        public string Process(Bitmap bitmap, bool isnum)
        {
            if (isDisposed)
                throw new ObjectDisposedException(nameof(OCRProcessor));

            // 2. 숫자 OCR 모드 설정 (한 번만 설정되도록 변경)
            if (isnum)
            {
                lock (lockObj)
                {
                    engine.SetVariable("tessedit_char_whitelist", "0123456789,./");
                }
            }

            // 3. OCR 수행
            using (var pix = PixConverter.ToPix(bitmap))
            {
                return engine.Process(pix).GetText().Trim();
            }
        }

        // 4. 엔진 리소스 해제 (Dispose 패턴 적용)
        public void Dispose()
        {
            if (!isDisposed)
            {
                lock (lockObj)
                {
                    engine?.Dispose();
                    engine = null;
                    isDisposed = true;
                }
            }
        }
    }
}
