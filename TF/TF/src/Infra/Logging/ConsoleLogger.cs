using System;

namespace TF.src.Infra.Logging
{
    public class ConsoleLogger : IConsoleLogger
    {
        private readonly object _lock = new();
        private static string DataAtual => DateTimeOffset.Now.ToString("yyyy-MM-dd HH:mm:ss");

        public void Info(string mensagem)
        {
            lock (_lock)
            {
                Console.BackgroundColor = ConsoleColor.DarkMagenta;
                Console.ForegroundColor = ConsoleColor.White;
                Console.WriteLine($"[INFORMACAO] [{DataAtual}]");
                Console.ResetColor();
                Console.WriteLine(mensagem);
            }
        }

        public void Aviso(string mensagem)
        {
            lock (_lock)
            {
                Console.BackgroundColor = ConsoleColor.Yellow;
                Console.ForegroundColor = ConsoleColor.Black;
                Console.WriteLine($"[AVISO!] [{DataAtual}]");
                Console.ResetColor();
                Console.WriteLine(mensagem);
            }
        }

        public void Erro(string mensagem, Exception? excessao = null)
        {
            lock (_lock)
            {
                Console.BackgroundColor = ConsoleColor.Red;
                Console.ForegroundColor = ConsoleColor.White;
                Console.WriteLine($"[ERRO!!!] [{DataAtual}]");
                Console.ResetColor();
                Console.WriteLine(mensagem);

                if (excessao != null)
                {
                    Console.BackgroundColor = ConsoleColor.DarkRed;
                    Console.ForegroundColor = ConsoleColor.White;
                    Console.WriteLine("Detalhes da exceção:");
                    Console.WriteLine(excessao.ToString());
                    Console.ResetColor();
                }
            }
        }
    }
}