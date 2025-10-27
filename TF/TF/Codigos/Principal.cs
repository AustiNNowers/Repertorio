// Bibliotecas
using System;
using System.Text;
using System.Text.Json;

namespace TF
{
  class Principal
  {
    static void Main(string[] args)
    {
      var config = CarregarConfiguracoes();

      Console.WriteLine("Token: " + config.GetProperty("Informacoes_Token").GetProperty("Token").GetString());
    }

    //Carregar informações do JSON para fazer as execuções.
    static JsonElement CarregarConfiguracoes()
    {
      string jsonEmTexto = File.ReadAllText("configuracoes.json");

      JsonElement json = JsonSerializer.Deserialize<JsonElement>(jsonEmTexto);

      // Verificar se o token do JSON existe e se ainda é valido.
      if (Verificar_Token.)
      {
        return json;
      }
      else
      {
        return CarregarConfiguracoes();
      }
    }
  }
}

