// Bibliotecas
using System;
using System.Text;
using System.Text.Json;

namespace TF.Codigos
{
  class Principal
  {
    static void Main(string[] args)
    {
      var config = CarregarConfiguracoes();

      Requisitor requisitor = new Requisitor(config);

      
    }

    //Carregar informações do JSON para fazer as execuções.
    static JsonElement CarregarConfiguracoes()
    {
      string jsonEmTexto = File.ReadAllText("configuracoes.json");
      JsonElement json = JsonSerializer.Deserialize<JsonElement>(jsonEmTexto);

      Verificar_Token verificador = new Verificar_Token();

      // Verificar se o token do JSON existe e se ainda é valido.
      if (verificador.VerificarToken())
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

