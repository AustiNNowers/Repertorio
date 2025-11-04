using System;
using System.Collections.Generic;
using System.Data;
using System.Linq;
using System.Net.Mime;
using System.Text.Json;
using System.Threading.Tasks;

using TF.src.Domain.Ports;
using TF.src.Infra.Configuracoes;
using TF.src.Infra.Logging;

namespace TF.src.Infra.Autenticacao
{
    public class ProvedorToken(HttpClient http, IArmazenagemToken armazenar, RootConfig config, IConsoleLogger log) : IProvedorToken
    {
        private readonly HttpClient _http = http;
        private readonly IArmazenagemToken _armazenar = armazenar;
        private readonly RootConfig _config = config;
        private readonly IConsoleLogger _log = log;

        public async Task<string> GerarToken(CancellationToken comando = default)
        {
            var token = await _armazenar.ObterToken(comando);
            if (token is not null && DateTime.ParseExact(token.Expiracao, "dd/MM/yyyy HH:mm:ss", null) > DateTime.Now) return token.Token;

            await RenovarToken(comando);
            var renovado = await _armazenar.ObterToken(comando) ?? throw new InvalidOperationException("Falha ao obter token.");
            return renovado.Token;
        }

        public async Task RenovarToken(CancellationToken comando = default)
        {
            var formato = new Dictionary<string, string>
            {
                ["grant_type"] = _config.Credenciais.Grant_type,
                ["username"] = _config.Credenciais.Username,
                ["password"] = _config.Credenciais.Password,
                ["client_id"] = _config.Credenciais.Client_id,
                ["client_secret"] = _config.Credenciais.Client_secret
            };

            using var requisicao = new HttpRequestMessage(HttpMethod.Post, _config.UrlToken) { Content = new FormUrlEncodedContent(formato) };

            foreach (var header in _config.HeadersToken) requisicao.Headers.TryAddWithoutValidation(header.Key, header.Value);

            using var resposta = await _http.SendAsync(requisicao, comando);
            resposta.EnsureSuccessStatusCode();
            _log.Info("[Auth] Requisição com sucesso");

            var json = await resposta.Content.ReadAsStringAsync(comando);
            using var doc = JsonDocument.Parse(json);

            var acesso = doc.RootElement.GetProperty("access_token").GetString() ?? "";

            await _armazenar.SalvarToken(new TokenInfo(acesso, DateTime.Now.ToString("dd/MM/yyyy HH:mm:ss")), comando);
            _log.Info("[Auth] Token salvo");
        }
    }
}