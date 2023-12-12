# acr-regex

Extensao que verifica uma serie de regex sobre o conteudo do merge request, existe dois tipos de vaidacoes<br>
Regex sobre o titulo do merge request: Nesse caso se algum regex da lista nao de match sobre o titulo do merge, ira adicionar um comentario. Para esse caso o type sera MERGE_TITLE<br>
Regex sobre os arquivos alterados: Nesse caso se algum regex da lista de match sobre o conteudo de algum arquivo, ira adicionar um comentario. Para esse caso o type sera MERGE_FILE_CONTENT

1. Atributo data e uma lista de objetos, aonde cada objeto se refere a uma validacao
2. Atributo type dentro do objeto da lista, se refere ao tipo de validacao, se valida o titulo ou o conteudo dos arquivos
3. Atributo message dentro do objeto da lista, se refere ao comentario que deve ser adicionado ao merge request
4. Atributo inverted dentro do objeto da lista, se refere a inverter a validacao, ou seja para dizer que deve conter ou nao deve conter o regex no arquivo
5. Atributo regexFile dentro do objeto da lista, se refere a lista de regex para verificar os arquivos que devem verificar o conteudo
6. Atributo regex dentro do objeto da lista, se refere a lista de regex que devem ser verificados para adicionar ou nao o comentario no merge request
7. Atributo diffType dentro do objeto da lista, se refere a qual o tipo de diff a validação deve ser executada, sendo CREATE para novo arquivo, UPDATE para arquivo já existente, e quando não informado assume CREATE e UPDATE, ou seja ira executar indiferente se o arquivo é novo ou não

Arquivo config.json

```json
{
  "data": [
    {
      "type": "MERGE_FILE_CONTENT",
      "message": "",
      "inverted": false,
      "diffType": [
        "CREATE",
        "UPDATE"
      ],
      "regexFile": [
        ""
      ],
      "regex": [
        ""
      ]
    },
    {
      "type": "MERGE_TITLE",
      "message": "",
      "regex": [
        ""
      ]
    }
  ]
}
```

