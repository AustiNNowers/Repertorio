using System;
using System.Text;
using System.Text.Json;
using System.Net;
using System.Net.Http;
using System.Net.Http.Headers;

namespace TF
{
    public class Verificar_Token
    {
        DateTime data_atual = DateTime.Now;

        public bool VerificarToken(JsonElement json)
        {
            if (json.GetProperty("Informacoes_Token").GetProperty("Token").GetString() == string.Empty)
            {
                Criar_Token();

                return false;
            }
            else if ((DateTime.Parse(json.GetProperty("Informacoes_Token").GetProperty("Data_Gerada").GetString()) - data_atual) > TimeSpan.FromHours(24)) {
                Criar_Token();

                return false;
            }
            else
            {
                return true;
            }
        }

        private void Criar_Token()
        {
            string jsonEmTexto = File.ReadAllText("configuracoes.json");
            JsonElement json = JsonSerializer.Deserialize<JsonElement>(jsonEmTexto);

            var json_envio = json.GetProperty("Credeciais");
            var content = new StringContent(jsonEmTexto, Encoding.UTF8, json.GetProperty("TF_Token_header").GetProperty("Content-Type").GetString());
            var cliente = new HttpClient();

            var resposta = cliente.PostAsync(json.GetProperty("TF_Token_Url").GetString(), content);

            if (resposta.IsCompletedSuccessfully)
            {
                Console.WriteLine("Status: " + resposta.Status);
                Console.WriteLine("Resposta dada: " + resposta.Result.ToString());
            }
        }
    }
}