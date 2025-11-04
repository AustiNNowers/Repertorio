

namespace TF.src.Infra.Configuracoes
{
    public interface IConfigProvider
    {
        Task<RootConfig> CarregarConfiguracao(CancellationToken comando = default);
    }

    public class RootConfig
    {
        public required string UrlTF { get; set; }
        public required string UrlPhp { get; set; }
        public required string UrlToken { get; set; }

        public required Dictionary<string, string> HeadersTF { get; set; }
        public required Dictionary<string, string> HeadersPhp { get; set; }
        public required Dictionary<string, string> HeadersToken { get; set; }

        public required CredenciaisMeta Credenciais { get; set; }

        public required TokenMeta InformacoesToken { get; set; }

        public required Dictionary<string, TabelaMeta> Tabelas { get; set; }
    }

    public class TabelaMeta
    {
        public required string NomeTabela { get; set; }
        public required string UrlFinal { get; set; }
        public required string UltimaAtualizacao { get; set; }
    }

    public class TokenMeta
    {
        public required string Token { get; set; }
        public required string DataGerada { get; set; }
        public required string DataExpirada { get; set; }
    }

    public class CredenciaisMeta
    {
        public required string Grant_type { get; set; }
        public required string Username { get; set; }
        public required string Password { get; set; }
        public required string Client_id { get; set; }
        public required string Client_secret { get; set; }
    }
}