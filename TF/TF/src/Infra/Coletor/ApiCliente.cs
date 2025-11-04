using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

using TF.src.Infra.Autenticacao;
using TF.src.Infra.Logging;
using TF.src.Infra.Modelo;

namespace TF.src.Infra.Coletor
{
    public class ApiCliente
    (
        HttpClient http,
        IProvedorToken provedorToken,
        IConsoleLogger log,
        TimeSpan intervalo,
        SemaphoreSlim gate,
        string urlBase,
        IReadOnlyDictionary<string, string> headers,
        TimeSpan? tamanhoJanelaBusca = null,
        TimeSpan? margemVerificacao = null
    ) : IColetorDados
    {
        private DateTime _dataAtual = DateTime.UtcNow;
        private readonly HttpClient _http = http;
        private readonly IProvedorToken _provedorToken = provedorToken;
        private readonly IConsoleLogger _log = log;
        private readonly TimeSpan _intervalo = intervalo;
        private readonly TimeSpan? _tamanhoJanelaBusca = tamanhoJanelaBusca > TimeSpan.FromDays(3) ? TimeSpan.FromDays(3) : tamanhoJanelaBusca ?? TimeSpan.FromDays(1);
        private readonly TimeSpan? _margemVerificacao = margemVerificacao ?? TimeSpan.FromDays(3);
        private readonly SemaphoreSlim _gate = gate;
        private readonly string _urlBase = urlBase;
        private readonly IReadOnlyDictionary<string, string> _headers = headers;

        private long _lastTicks;

        public async IAsyncEnumerable<ApiLinha[]> ColetarDados(
            string urlFinal,
            string dataAtual,
            CancellationToken comando = default
        )
        {
            var dataInicio = DateTime.ParseExact(dataAtual, "yyyy-MM-dd HH:mm:ss", null) - _margemVerificacao;

            while (dataInicio < _dataAtual)
            {
                await LimiteRequisicao(comando);

                var dataFim = (dataInicio + tamanhoJanelaBusca) > _dataAtual ? _dataAtual : (dataInicio + tamanhoJanelaBusca);
            }
        }

        private async Task LimiteRequisicao(CancellationToken comando)
        {
            await _gate.WaitAsync(comando);

            try
            {
                var agora = DateTime.UtcNow.Ticks;
                var tempoDecorrido = TimeSpan.FromTicks(agora - Interlocked.Read(ref _lastTicks));
                if (tempoDecorrido < _intervalo) await Task.Delay(_intervalo - tempoDecorrido, comando);
                Interlocked.Exchange(ref _lastTicks, DateTime.UtcNow.Ticks);
            }
            finally
            {
                _gate.Release();
            }
        }
        
        private static string ConstrutorUrl(string urlFinal, )
        {
            
        }
    }
}