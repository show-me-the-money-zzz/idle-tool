namespace IdleTool.Addon
{
    public class Singleton<T> where T : new()
    {
        private static readonly object lockObj = new object();
        private static T instance;

        public static T Instance
        {
            get
            {
                lock (lockObj)
                {
                    if (instance == null)
                    {
                        instance = new T();
                    }
                    return instance;
                }
            }
        }

        protected Singleton() { } // 🔹 protected 생성자로 상속 가능하도록 변경
    }
}
