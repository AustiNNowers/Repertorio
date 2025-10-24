using System;
using System.Text;
using System.Text.Json;

namespace TF
{
  class Program
  {
    static void Main(string[] args)
    {
      var config = CarregarConfiguracoes();

      Console.WriteLine("Link do TF: " + config.GetProperty("TF_API_BaseUrl").GetString());
    }

    static JsonElement CarregarConfiguracoes()
    {
      string jsonEmTexto = File.ReadAllText("configuracoes.json");

      JsonElement json = JsonSerializer.Deserialize<JsonElement>(jsonEmTexto);

      if (VerificarToken(json))
      {
        return json;
      } else {
        return CriarToken(json);
      }
    }

    static bool VerificarToken(JsonElement json)
    {
      if (json.GetProperty("Informacoes_Token").GetProperty("Token").GetString() == string.Empty)
      {
        return false;
      }
      else
      {
        return true;
      }
    }

    static JsonElement CriarToken(JsonElement json)
    {
      

      return json;   
    }
  }
}

