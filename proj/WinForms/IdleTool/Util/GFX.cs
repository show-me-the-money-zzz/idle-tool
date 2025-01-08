namespace IdleTool.Util
{
    using System;
    using System.Drawing;
    using System.Drawing.Imaging;
    using System.Runtime.InteropServices;

    using Emgu.CV;
    using Emgu.CV.CvEnum;

    public static class GFX
    {
        ////MemoryStream 기반 변환: 간단하고 안정적인 방법으로 일반적으로 권장.. by ChatGPT
        //static Mat BitmapToMat(Bitmap __bitmap)
        //{
        //    // Bitmap을 MemoryStream에 저장
        //    using (var ms = new System.IO.MemoryStream())
        //    {
        //        __bitmap.Save(ms, System.Drawing.Imaging.ImageFormat.Bmp);
        //        byte[] bitmapData = ms.ToArray();

        //        // byte[] 데이터를 Mat으로 변환
        //        Mat mat = new Mat();
        //        mat = Mat.FromImageData(bitmapData, Emgu.CV.CvEnum.ImreadModes.Color);
        //        return mat;
        //    }
        //}

        //BitmapData.Scan0 기반 변환: 고성능이 필요하거나 MemoryStream을 피하고 싶을 때 유용.. by ChatGPT
        //public static Mat Bitmap_To_Mat_Direct__ERROR(Bitmap __bitmap)
        //{
        //    // Bitmap 데이터를 잠금
        //    Rectangle rect = new Rectangle(0, 0, __bitmap.Width, __bitmap.Height);
        //    System.Drawing.Imaging.BitmapData bitmapData = __bitmap.LockBits(rect,
        //        System.Drawing.Imaging.ImageLockMode.ReadOnly,
        //        System.Drawing.Imaging.PixelFormat.Format24bppRgb);

        //    // Mat 객체 생성 (OpenCV는 기본적으로 BGR 포맷을 사용)
        //    Mat mat = new Mat(__bitmap.Height, __bitmap.Width, Emgu.CV.CvEnum.DepthType.Cv8U, 3);

        //    // Bitmap의 데이터를 Mat로 복사
        //    CvInvoke.cvCopy(bitmapData.Scan0, mat.DataPointer, IntPtr.Zero);

        //    // Bitmap 잠금 해제
        //    __bitmap.UnlockBits(bitmapData);

        //    return mat;
        //}

        /* (by ChatGPT).. Mat Bitmap_To_Mat_Direct__ERROR(Bitmap) 보완
         * 코드 설명
            BitmapData.Scan0에서 데이터 복사:

            Bitmap.LockBits로 Scan0 포인터를 얻어 이미지 데이터를 읽습니다.
            Marshal.Copy를 사용하여 픽셀 데이터를 배열(byte[])로 복사합니다.
            Mat.DataPointer로 데이터 복사:

            Mat.DataPointer는 Mat 객체의 메모리 주소를 나타냅니다.
            Marshal.Copy를 사용하여 byte[] 데이터를 Mat 객체의 메모리로 복사합니다.
            예외 처리:

            try-finally 블록을 사용하여 Bitmap.UnlockBits를 항상 호출하도록 보장합니다.
            PixelFormat 지원:

            현재 코드에서는 Format24bppRgb, Format32bppArgb, Format8bppIndexed 등을 처리할 수 있습니다.
            다른 포맷을 처리하려면 추가적인 변환 로직이 필요할 수 있습니다.

         * 주요 수정 사항
            CvInvoke.cvCopy 제거:
            이 메서드는 잘못된 호출이며 제거되었습니다.
            Marshal.Copy를 사용한 안전한 데이터 복사:
            Emgu CV의 Mat 데이터 영역으로 직접 복사합니다.

         * 주의사항
            DPI 및 해상도 고려:

            고해상도 DPI 설정에서 데이터의 크기가 예상과 다를 수 있으니 이를 확인하세요.
            성능:

            메모리 복사 작업은 큰 이미지를 처리할 때 성능 저하를 유발할 수 있습니다. 성능이 중요한 경우 네이티브 OpenCV 함수를 사용하는 방법도 고려할 수 있습니다.
            지원 포맷 제한:

            이 코드는 일반적인 RGB 포맷(Bitmap)만 처리하며, 특수한 포맷은 변환이 필요합니다.
         */
        public static Mat Bitmap_To_Mat_Direct(Bitmap bitmap)
        {//안전하고 정확한 메모리 복사
            // Bitmap 크기 및 포맷 확인
            int width = bitmap.Width;
            int height = bitmap.Height;
            PixelFormat pixelFormat = bitmap.PixelFormat;

            // 채널 수 계산
            int channels = Image.GetPixelFormatSize(pixelFormat) / 8; // PixelFormat에 따른 채널 계산
            if (channels != 1 && channels != 3 && channels != 4)
            {
                throw new NotSupportedException("지원되지 않는 PixelFormat입니다.");
            }

            // Bitmap 데이터를 잠금
            Rectangle rect = new Rectangle(0, 0, width, height);
            BitmapData bitmapData = bitmap.LockBits(rect, ImageLockMode.ReadOnly, pixelFormat);

            try
            {
                // Mat 객체 생성
                Mat mat = new Mat(height, width, DepthType.Cv8U, channels);

                // Bitmap 데이터를 Mat로 복사
                int dataSize = Math.Abs(bitmapData.Stride) * height;
                byte[] data = new byte[dataSize];
                Marshal.Copy(bitmapData.Scan0, data, 0, dataSize);

                // Mat에 데이터 복사
                Marshal.Copy(data, 0, mat.DataPointer, dataSize);

                return mat;
            }
            finally
            {
                // Bitmap 잠금 해제
                bitmap.UnlockBits(bitmapData);
            }
        }
    }
}
