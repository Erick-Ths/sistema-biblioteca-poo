# 📚 Sistema de Gerenciamento de Biblioteca — POO em Python

Atividade prática de Programação Orientada a Objetos.

## O que o programa faz

É um sistema de controle de empréstimos de uma biblioteca, via terminal (CLI).
Permite:

- Cadastrar itens do acervo: **Livros**, **Revistas** e **DVDs** (cada um com prazo de empréstimo e multa diária diferentes).
- Cadastrar usuários.
- Realizar empréstimos (verifica disponibilidade do item).
- Devolver itens (calcula multa automaticamente em caso de atraso).
- Listar acervo, usuários e empréstimos ativos.
- Os dados ficam salvos em `biblioteca_dados.json`, então nada se perde ao fechar o programa.

## Como executar

Requer apenas Python 3 (nenhuma biblioteca externa):

```bash
python3 biblioteca_poo.py
```

Depois é só seguir o menu numérico que aparece no terminal.

## Conceitos de POO utilizados

| Conceito | Onde aparece |
|---|---|
| **Abstração** | `ItemAcervo` é uma classe abstrata (`ABC`), com os métodos `dias_emprestimo()` e `multa_diaria()` declarados como `@abstractmethod`. Ela nunca é instanciada diretamente. |
| **Herança** | `Livro`, `Revista` e `DVD` herdam de `ItemAcervo` e reaproveitam toda a lógica comum (status, código, título, etc). |
| **Polimorfismo** | A classe `Emprestimo` chama `item.dias_emprestimo()` e `item.multa_diaria()` sem saber se o item é um Livro, Revista ou DVD — cada subclasse responde de um jeito diferente. |
| **Encapsulamento** | `Usuario.__matricula` é um atributo privado (acessado só via `@property`); `ItemAcervo.disponivel` tem um *setter* que valida o tipo do valor antes de aceitar. |
| **Composição** | `Emprestimo` é composto por um `Usuario` e um `ItemAcervo`; `Biblioteca` agrega listas de `ItemAcervo`, `Usuario` e `Emprestimo`, coordenando as regras de negócio entre eles. |

## Estrutura do código

- `ItemAcervo` (abstrata) → `Livro`, `Revista`, `DVD`
- `Usuario`
- `Emprestimo`
- `Biblioteca` (classe principal, gerencia tudo e persiste em JSON)
- Funções `*_cli` e `main()` → interface de terminal

## Tratamento de erros

Operações inválidas (código duplicado, item indisponível, usuário/item inexistente, JSON corrompido) lançam `ValueError` tratado na camada de CLI, exibindo uma mensagem amigável em vez de quebrar o programa.
