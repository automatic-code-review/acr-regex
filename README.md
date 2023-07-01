# acr-regex

Extensao que verifica uma serie de regex sobre o conteudo do merge request, existe dois tipos de vaidacoes

1. Regex sobre o titulo do merge request: Nesse caso se algum regex da lista nao de match sobre o titulo do merge, ira adicionar um comentario. Para esse caso o type sera MERGE_TITLE
2. Regex sobre os arquivos alterados: Nesse caso se algum regex da lista de match sobre o conteudo de algum arquivo, ira adicionar um comentario. Para esse caso o type sera MERGE_FILE_CONTENT

Arquivo config.json

```json
{
  "data": [
    {
      "type": "MERGE_FILE_CONTENT",
      "message": "",
      "inverted": false,
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

