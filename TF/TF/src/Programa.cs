using System;
using System.Threading;

using TF.src.Domain.Ports;
using TF.src.Infra.Logging;
using TF.src.Infra.Configuracoes;
using TF.src.Infra.Armazenagem;
using TF.src.Infra.Autenticacao;

Console.OutputEncoding = System.Text.Encoding.UTF8;

namespace TF.src
{
    public class Programa
    {
        public static async Task Main(string[] args)
        {
            // Inicialização do logger e do programa.
            var logger = new ConsoleLogger();
            logger.Info("=== Início do Programa ===");

            // Cancelamento usando Ctrl+C no console.
            var cts = new CancellationTokenSource();
            Console.CancelKeyPress += (_, e) =>
            {
                e.Cancel = true;
                logger.Aviso("[Principal] Sinal de cancelamento recebido. Encerrando o programa...");
                cts.Cancel();
            };

            // Configuração do JSON
            IConfigProvider configuracaoProvedor = new ConfigJson(args.Length > 0 ? args[0] : "configuracoes.json");
            var config = await configuracaoProvedor.CarregarConfiguracao(cts.Token);

            IGuardarDados guardarDados = new GuardarDadosJson("configuracoes.json");
            logger.Info("[Principal] Configurações carregadas com sucesso. ||| GuardarDadosJson foi ativado.");

            // Token
            IArmazenagemToken armazenagemToken = new GerenciadorArmazenagemToken(
                new GuardarTokenRemoto(),
                new GuardarTokenJson("configuracoes.json")
            );

            var httpApi = new HttpClient { Timeout = TimeSpan.FromSeconds(15) };
            var httpPhp = new HttpClient { Timeout = TimeSpan.FromSeconds(3) };

        }
    }
}