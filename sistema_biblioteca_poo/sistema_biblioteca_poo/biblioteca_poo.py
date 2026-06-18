"""
Sistema de Gerenciamento de Biblioteca - POO em Python
Atividade Prática - Programação Orientada a Objetos

Conceitos de POO aplicados:
- Abstração: classe abstrata ItemAcervo (ABC) define o contrato comum.
- Herança: Livro, Revista e DVD herdam de ItemAcervo.
- Polimorfismo: cada subclasse implementa dias_emprestimo()/multa_diaria()
  de forma diferente, e o sistema usa esses métodos sem saber o tipo exato.
- Encapsulamento: atributos protegidos/privados acessados via @property,
  com validação em setters (ex: Usuario.__matricula, ItemAcervo.disponivel).
- Composição: Emprestimo é composto por um Usuario e um ItemAcervo;
  Biblioteca agrega listas de Usuario, ItemAcervo e Emprestimo.
"""

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
import json
import os


# ===================== ITENS DO ACERVO (ABSTRAÇÃO / HERANÇA) =====================

class ItemAcervo(ABC):
    """Classe abstrata que representa um item do acervo da biblioteca."""

    def __init__(self, titulo, autor_ou_editora, codigo):
        self._titulo = titulo
        self._autor_ou_editora = autor_ou_editora
        self._codigo = codigo
        self._disponivel = True

    @property
    def titulo(self):
        return self._titulo

    @property
    def codigo(self):
        return self._codigo

    @property
    def disponivel(self):
        return self._disponivel

    @disponivel.setter
    def disponivel(self, valor):
        if not isinstance(valor, bool):
            raise ValueError("Disponibilidade deve ser True ou False.")
        self._disponivel = valor

    @abstractmethod
    def dias_emprestimo(self):
        """Quantidade de dias que o item pode ficar emprestado."""

    @abstractmethod
    def multa_diaria(self):
        """Valor da multa por dia de atraso na devolução."""

    def __str__(self):
        status = "Disponível" if self._disponivel else "Emprestado"
        return f"[{self._codigo}] {self._titulo} - {self._autor_ou_editora} ({status})"

    def to_dict(self):
        return {
            "tipo": self.__class__.__name__,
            "titulo": self._titulo,
            "autor_ou_editora": self._autor_ou_editora,
            "codigo": self._codigo,
            "disponivel": self._disponivel,
        }


class Livro(ItemAcervo):
    def dias_emprestimo(self):
        return 14

    def multa_diaria(self):
        return 1.00


class Revista(ItemAcervo):
    def dias_emprestimo(self):
        return 7

    def multa_diaria(self):
        return 0.50


class DVD(ItemAcervo):
    def dias_emprestimo(self):
        return 5

    def multa_diaria(self):
        return 2.00


def criar_item_por_tipo(tipo, titulo, autor_ou_editora, codigo):
    """Fábrica simples para recriar o item correto a partir dos dados salvos."""
    classes = {"Livro": Livro, "Revista": Revista, "DVD": DVD}
    classe = classes.get(tipo)
    if not classe:
        raise ValueError(f"Tipo de item desconhecido: {tipo}")
    return classe(titulo, autor_ou_editora, codigo)


# ===================== USUÁRIO (ENCAPSULAMENTO) =====================

class Usuario:
    def __init__(self, nome, matricula):
        self._nome = nome
        self.__matricula = matricula  # atributo privado (name mangling)

    @property
    def nome(self):
        return self._nome

    @property
    def matricula(self):
        return self.__matricula

    def __str__(self):
        return f"{self._nome} (matrícula: {self.__matricula})"

    def to_dict(self):
        return {"nome": self._nome, "matricula": self.__matricula}


# ===================== EMPRÉSTIMO (COMPOSIÇÃO) =====================

class Emprestimo:
    """Um Emprestimo é composto por um Usuario e um ItemAcervo."""

    def __init__(self, usuario: Usuario, item: ItemAcervo, data_emprestimo=None):
        self.usuario = usuario
        self.item = item
        self.data_emprestimo = data_emprestimo or datetime.now()
        self.data_devolucao_prevista = self.data_emprestimo + timedelta(
            days=item.dias_emprestimo()  # polimorfismo: cada item sabe seu prazo
        )
        self.data_devolucao_real = None

    def devolver(self):
        self.data_devolucao_real = datetime.now()
        self.item.disponivel = True
        return self.calcular_multa()

    def calcular_multa(self):
        data_referencia = self.data_devolucao_real or datetime.now()
        dias_atraso = (data_referencia - self.data_devolucao_prevista).days
        if dias_atraso > 0:
            return round(dias_atraso * self.item.multa_diaria(), 2)  # polimorfismo
        return 0.0

    def esta_atrasado(self):
        return self.data_devolucao_real is None and datetime.now() > self.data_devolucao_prevista

    def __str__(self):
        prazo = self.data_devolucao_prevista.strftime("%d/%m/%Y")
        situacao = "ATRASADO" if self.esta_atrasado() else "Em dia"
        return f"{self.item.titulo} -> {self.usuario.nome} | devolver até {prazo} | {situacao}"


# ===================== BIBLIOTECA (CLASSE PRINCIPAL / AGREGAÇÃO) =====================

class Biblioteca:
    ARQUIVO_DADOS = "biblioteca_dados.json"

    def __init__(self):
        self.acervo = []        # lista de ItemAcervo
        self.usuarios = []      # lista de Usuario
        self.emprestimos = []   # lista de Emprestimo
        self.carregar_dados()

    # ---------- Cadastro ----------
    def cadastrar_item(self, item: ItemAcervo):
        if any(i.codigo == item.codigo for i in self.acervo):
            raise ValueError("Já existe um item com esse código.")
        self.acervo.append(item)
        self.salvar_dados()

    def cadastrar_usuario(self, usuario: Usuario):
        if any(u.matricula == usuario.matricula for u in self.usuarios):
            raise ValueError("Já existe um usuário com essa matrícula.")
        self.usuarios.append(usuario)
        self.salvar_dados()

    # ---------- Busca ----------
    def buscar_item(self, codigo):
        return next((item for item in self.acervo if item.codigo == codigo), None)

    def buscar_usuario(self, matricula):
        return next((u for u in self.usuarios if u.matricula == matricula), None)

    # ---------- Empréstimos ----------
    def realizar_emprestimo(self, codigo_item, matricula_usuario):
        item = self.buscar_item(codigo_item)
        usuario = self.buscar_usuario(matricula_usuario)

        if item is None:
            raise ValueError("Item não encontrado.")
        if usuario is None:
            raise ValueError("Usuário não encontrado.")
        if not item.disponivel:
            raise ValueError("Item já está emprestado.")

        item.disponivel = False
        emprestimo = Emprestimo(usuario, item)
        self.emprestimos.append(emprestimo)
        self.salvar_dados()
        return emprestimo

    def devolver_item(self, codigo_item):
        for emprestimo in self.emprestimos:
            if emprestimo.item.codigo == codigo_item and emprestimo.data_devolucao_real is None:
                multa = emprestimo.devolver()
                self.salvar_dados()
                return multa
        raise ValueError("Não há empréstimo ativo para esse item.")

    def listar_emprestimos_ativos(self):
        return [e for e in self.emprestimos if e.data_devolucao_real is None]

    # ---------- Persistência (JSON) ----------
    def salvar_dados(self):
        dados = {
            "acervo": [item.to_dict() for item in self.acervo],
            "usuarios": [u.to_dict() for u in self.usuarios],
        }
        with open(self.ARQUIVO_DADOS, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)

    def carregar_dados(self):
        if not os.path.exists(self.ARQUIVO_DADOS):
            return
        try:
            with open(self.ARQUIVO_DADOS, "r", encoding="utf-8") as f:
                dados = json.load(f)
            for d in dados.get("acervo", []):
                item = criar_item_por_tipo(d["tipo"], d["titulo"], d["autor_ou_editora"], d["codigo"])
                item.disponivel = d["disponivel"]
                self.acervo.append(item)
            for d in dados.get("usuarios", []):
                self.usuarios.append(Usuario(d["nome"], d["matricula"]))
        except (json.JSONDecodeError, KeyError):
            print("⚠️  Não foi possível carregar dados anteriores. Iniciando do zero.")


# ===================== INTERFACE CLI =====================

def menu():
    print("\n===== BIBLIOTECA - MENU =====")
    print("1. Cadastrar item (livro/revista/DVD)")
    print("2. Cadastrar usuário")
    print("3. Listar acervo")
    print("4. Listar usuários")
    print("5. Realizar empréstimo")
    print("6. Devolver item")
    print("7. Listar empréstimos ativos")
    print("0. Sair")


def cadastrar_item_cli(biblioteca):
    print("\nTipos: 1-Livro  2-Revista  3-DVD")
    tipo = input("Escolha o tipo: ").strip()
    titulo = input("Título: ").strip()
    autor = input("Autor/Editora: ").strip()
    codigo = input("Código (único): ").strip()

    mapa_tipos = {"1": Livro, "2": Revista, "3": DVD}
    classe = mapa_tipos.get(tipo)
    if not classe:
        print("Tipo inválido.")
        return
    try:
        biblioteca.cadastrar_item(classe(titulo, autor, codigo))
        print("Item cadastrado com sucesso!")
    except ValueError as e:
        print(f"Erro: {e}")


def cadastrar_usuario_cli(biblioteca):
    nome = input("Nome: ").strip()
    matricula = input("Matrícula (única): ").strip()
    try:
        biblioteca.cadastrar_usuario(Usuario(nome, matricula))
        print("Usuário cadastrado com sucesso!")
    except ValueError as e:
        print(f"Erro: {e}")


def listar_acervo_cli(biblioteca):
    if not biblioteca.acervo:
        print("Acervo vazio.")
    for item in biblioteca.acervo:
        print(item)


def listar_usuarios_cli(biblioteca):
    if not biblioteca.usuarios:
        print("Nenhum usuário cadastrado.")
    for usuario in biblioteca.usuarios:
        print(usuario)


def emprestimo_cli(biblioteca):
    codigo = input("Código do item: ").strip()
    matricula = input("Matrícula do usuário: ").strip()
    try:
        emprestimo = biblioteca.realizar_emprestimo(codigo, matricula)
        print(f"Empréstimo realizado! {emprestimo}")
    except ValueError as e:
        print(f"Erro: {e}")


def devolucao_cli(biblioteca):
    codigo = input("Código do item a devolver: ").strip()
    try:
        multa = biblioteca.devolver_item(codigo)
        if multa > 0:
            print(f"Item devolvido com atraso. Multa: R$ {multa:.2f}")
        else:
            print("Item devolvido dentro do prazo. Sem multa.")
    except ValueError as e:
        print(f"Erro: {e}")


def listar_emprestimos_cli(biblioteca):
    ativos = biblioteca.listar_emprestimos_ativos()
    if not ativos:
        print("Nenhum empréstimo ativo.")
    for emprestimo in ativos:
        print(emprestimo)


def main():
    biblioteca = Biblioteca()
    acoes = {
        "1": cadastrar_item_cli,
        "2": cadastrar_usuario_cli,
        "3": listar_acervo_cli,
        "4": listar_usuarios_cli,
        "5": emprestimo_cli,
        "6": devolucao_cli,
        "7": listar_emprestimos_cli,
    }

    print("📚 Bem-vindo ao Sistema de Gerenciamento de Biblioteca!")
    while True:
        menu()
        opcao = input("Escolha uma opção: ").strip()
        if opcao == "0":
            print("Até logo!")
            break
        acao = acoes.get(opcao)
        if acao:
            acao(biblioteca)
        else:
            print("Opção inválida.")


if __name__ == "__main__":
    main()
