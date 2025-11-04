using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.Json;
using System.Threading.Tasks;

namespace TF.Codigos
{
    public class Requisitor
    {
        JsonElement configuracoes;

        public Requisitor(JsonElement configuracoes)
        {
            this.configuracoes = configuracoes;
        }

        private string ObterUltimaData(JsonElement tabela)
        {
            if (configuracoes.TryGetProperty("Ultima_Data", out JsonElement dataElement))
            {
                return dataElement.GetString();
            }
            else
            {
                return "2025-01-01";
            }

        }
    
        
    }
}