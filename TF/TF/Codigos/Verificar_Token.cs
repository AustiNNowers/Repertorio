using System.Text.Json;
using System.Text.Json.Nodes;

namespace TF.Codigos
{
    public class Verificar_Token
    {
        DateTime data_atual = DateTime.Now;
        
        private JsonElement json_para_verificar = JsonSerializer.Deserialize<JsonElement>(File.ReadAllText("configuracoes.json"));

        public bool VerificarToken()
        {
            if (
                json_para_verificar.GetProperty("Informacoes_Token").GetProperty("Token").GetString() == string.Empty ||
                (data_atual - DateTime.ParseExact(json_para_verificar.GetProperty("Informacoes_Token").GetProperty("Data_Gerada").GetString(), "MM/dd/yyyy HH:mm:ss", null)) > TimeSpan.FromHours(24)
                )
            {
                Criar_Token(json_para_verificar);

                return false;
            }
            else
            {
                return true;
            }
        }

        private static void Criar_Token(JsonElement json)
        {
            var credenciais = JsonSerializer.Deserialize<Dictionary<string, string>>(json.GetProperty("Credenciais").GetRawText());
            var content = new FormUrlEncodedContent(credenciais);
            var cliente = new HttpClient();

            var requisicao = new HttpRequestMessage(HttpMethod.Post, json.GetProperty("TF_Token_Url").GetString());

            content.Headers.ContentType = new System.Net.Http.Headers.MediaTypeHeaderValue(json.GetProperty("TF_Token_header").GetProperty("Content-Type").GetString());
            requisicao.Content = content;

            Console.WriteLine("Enviando requisição para gerar novo token...");
            Console.WriteLine("URL: " + json.GetProperty("TF_Token_Url").GetString());
            Console.WriteLine("Corpo da requisição: " + credenciais);
            Console.WriteLine("Headers da requisição: " + content.Headers.ToString());

            var resposta = cliente.Send(requisicao);

            if (resposta.IsSuccessStatusCode)
            {
                Console.WriteLine("Status: " + resposta.StatusCode);

                JsonNode atualizar_json = JsonNode.Parse(File.ReadAllText("configuracoes.json"));
                var resposta_json = JsonNode.Parse(resposta.Content.ReadAsStringAsync().Result);

                atualizar_json["Informacoes_Token"]["Token"] = resposta_json["access_token"].ToString();
                atualizar_json["Informacoes_Token"]["Data_Gerada"] = DateTime.Now.ToString("MM/dd/yyyy HH:mm:ss");

                File.WriteAllText("configuracoes.json", atualizar_json.ToJsonString(new JsonSerializerOptions { WriteIndented = true }));
            
                Console.WriteLine("Novo token gerado e salvo no arquivo de configurações.");
            } else
            {
                Console.WriteLine("Status: " + resposta.StatusCode);
                Console.WriteLine("Resposta dada: " + resposta.Content.ReadAsStringAsync().Result);
            }
        }
    }
}