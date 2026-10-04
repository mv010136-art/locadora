"""
Trabalho Prático 02 - Sistema de Gerenciamento de uma Locadora de Veículos
Curso: Análise e Desenvolvimento de Sistemas | Disciplina: Coding

Herança:
  Veiculo  <- Carro, Moto, Caminhao
  Cliente  <- PessoaFisica, PessoaJuridica
Composição:
  Contrato ◆── Condutor      (o condutor só existe dentro do contrato)
  Veiculo  ◆── Manutencao    (cada manutenção pertence a um único veículo)
Associação:
  Cliente ─── Contrato ─── Veiculo
"""
from abc import ABC, abstractmethod
from datetime import date, timedelta
from enum import Enum


class StatusContrato(Enum):
    ATIVO = "ativo"
    FINALIZADO = "finalizado"
    CANCELADO = "cancelado"


def _so_digitos(texto):
    return "".join(c for c in str(texto) if c.isdigit())


# ===========================================================================
# MANUTENÇÃO  (parte de Veiculo - COMPOSIÇÃO)
# ===========================================================================
class Manutencao:
    def __init__(self, data, tipo_servico, custo):
        self.data = data
        self.tipo_servico = tipo_servico
        self.custo = custo

    def descricao(self):
        return f"{self.data:%d/%m/%Y} - {self.tipo_servico} - R$ {self.custo:.2f}"

    def eh_custosa(self, limite=1000):
        return self.custo >= limite


# ===========================================================================
# VEÍCULOS (HERANÇA)
# ===========================================================================
class Veiculo(ABC):
    def __init__(self, placa, modelo, ano, valor_diaria):
        self.placa = placa
        self.modelo = modelo
        self.ano = ano
        self.valor_diaria = valor_diaria
        self._alugado = False
        self._manutencoes = []        # composição: o veículo cria as manutenções

    # --- composição com Manutencao ---
    def registrar_manutencao(self, data, tipo_servico, custo):
        self._manutencoes.append(Manutencao(data, tipo_servico, custo))

    def historico_manutencoes(self):
        return [m.descricao() for m in self._manutencoes]

    def custo_total_manutencoes(self):
        return sum(m.custo for m in self._manutencoes)

    # --- controle de disponibilidade ---
    def esta_disponivel(self):
        return not self._alugado

    def marcar_como_alugado(self):
        self._alugado = True

    def marcar_como_disponivel(self):
        self._alugado = False

    @abstractmethod
    def calcular_valor(self, dias):
        """Cada tipo de veículo calcula o valor do aluguel à sua maneira."""

    def exibir_ficha(self):
        return f"{self.modelo} ({self.ano}) - placa {self.placa} - diária R$ {self.valor_diaria:.2f}"


class Carro(Veiculo):
    def __init__(self, placa, modelo, ano, valor_diaria, numero_portas=4, combustivel="Flex"):
        super().__init__(placa, modelo, ano, valor_diaria)
        self.numero_portas = numero_portas
        self.combustivel = combustivel

    def calcular_valor(self, dias):
        return self.valor_diaria * dias

    def exibir_ficha(self):
        return f"[Carro] {super().exibir_ficha()} - {self.numero_portas} portas - {self.combustivel}"


class Moto(Veiculo):
    def __init__(self, placa, modelo, ano, valor_diaria, cilindradas=150, partida_eletrica=True):
        super().__init__(placa, modelo, ano, valor_diaria)
        self.cilindradas = cilindradas
        self.partida_eletrica = partida_eletrica

    def calcular_valor(self, dias):
        total = self.valor_diaria * dias
        return total * 0.90 if dias >= 7 else total   # regra ilustrativa: 10% off a partir de 7 dias

    def exibir_ficha(self):
        return f"[Moto] {super().exibir_ficha()} - {self.cilindradas}cc"


class Caminhao(Veiculo):
    TAXA_POR_EIXO = 40.0   # regra ilustrativa: adicional por eixo/dia

    def __init__(self, placa, modelo, ano, valor_diaria, capacidade_carga_kg=8000, numero_eixos=2):
        super().__init__(placa, modelo, ano, valor_diaria)
        self.capacidade_carga_kg = capacidade_carga_kg
        self.numero_eixos = numero_eixos

    def calcular_valor(self, dias):
        return (self.valor_diaria + self.TAXA_POR_EIXO * self.numero_eixos) * dias

    def exibir_ficha(self):
        return (f"[Caminhão] {super().exibir_ficha()} - "
                f"{self.capacidade_carga_kg} kg - {self.numero_eixos} eixos")


# ===========================================================================
# CLIENTES (HERANÇA)
# ===========================================================================
class Cliente(ABC):
    def __init__(self, nome, documento, telefone):
        self.nome = nome              # nome (PF) ou razão social (PJ)
        self.documento = documento    # CPF ou CNPJ
        self.telefone = telefone

    @abstractmethod
    def validar_documento(self):
        """Valida o formato do documento (CPF ou CNPJ)."""

    def atualizar_telefone(self, novo_telefone):
        self.telefone = novo_telefone

    def exibir_dados(self):
        return f"{self.nome} - doc. {self.documento} - tel. {self.telefone}"


class PessoaFisica(Cliente):
    def __init__(self, nome, cpf, telefone, data_nascimento):
        super().__init__(nome, cpf, telefone)
        self.data_nascimento = data_nascimento

    def validar_documento(self):
        return len(_so_digitos(self.documento)) == 11

    def idade(self):
        hoje = date.today()
        nasc = self.data_nascimento
        return hoje.year - nasc.year - ((hoje.month, hoje.day) < (nasc.month, nasc.day))


class PessoaJuridica(Cliente):
    def __init__(self, razao_social, cnpj, telefone, responsavel):
        super().__init__(razao_social, cnpj, telefone)
        self.responsavel = responsavel

    def validar_documento(self):
        return len(_so_digitos(self.documento)) == 14

    def exibir_dados(self):
        return f"{super().exibir_dados()} - responsável: {self.responsavel}"


# ===========================================================================
# CONDUTOR  (parte de Contrato - COMPOSIÇÃO)
# ===========================================================================
class Condutor:
    def __init__(self, nome, cnh, categoria="B"):
        self.nome = nome
        self.cnh = cnh
        self.categoria = categoria

    def validar_cnh(self):
        return len(_so_digitos(self.cnh)) == 11

    def exibir_dados(self):
        return f"Condutor {self.nome} - CNH {self.cnh} (cat. {self.categoria})"


# ===========================================================================
# CONTRATO  (ASSOCIA Cliente e Veiculo; COMPÕE Condutor)
# ===========================================================================
class Contrato:
    _proximo_id = 1

    def __init__(self, cliente, veiculo, data_inicio, data_termino_prevista,
                 nome_condutor, cnh_condutor, categoria_cnh="B"):
        if not veiculo.esta_disponivel():
            raise ValueError(f"Veículo {veiculo.placa} já está em um contrato ativo.")
        self.numero = Contrato._proximo_id
        Contrato._proximo_id += 1
        self.cliente = cliente            # associação (recebido de fora)
        self.veiculo = veiculo            # associação (recebido de fora)
        self.data_inicio = data_inicio
        self.data_termino_prevista = data_termino_prevista
        # COMPOSIÇÃO: o Contrato instancia o Condutor internamente.
        self.condutor = Condutor(nome_condutor, cnh_condutor, categoria_cnh)
        self.status = StatusContrato.ATIVO
        self.valor_total = self.calcular_valor_total()
        veiculo.marcar_como_alugado()

    def calcular_valor_total(self):
        dias = max((self.data_termino_prevista - self.data_inicio).days, 1)
        return self.veiculo.calcular_valor(dias)

    def finalizar(self):
        if self.status == StatusContrato.ATIVO:
            self.status = StatusContrato.FINALIZADO
            self.veiculo.marcar_como_disponivel()

    def cancelar(self):
        if self.status == StatusContrato.ATIVO:
            self.status = StatusContrato.CANCELADO
            self.veiculo.marcar_como_disponivel()

    def excluir(self):
        """Excluir o contrato elimina também o condutor (composição)."""
        self.cancelar()
        self.condutor = None

    def exibir_resumo(self):
        condutor = self.condutor.exibir_dados() if self.condutor else "sem condutor"
        return (f"Contrato #{self.numero} | {self.cliente.nome} | {self.veiculo.modelo} | "
                f"{self.data_inicio:%d/%m/%Y} a {self.data_termino_prevista:%d/%m/%Y} | "
                f"R$ {self.valor_total:.2f} | {self.status.value} | {condutor}")


# ===========================================================================
# DEMONSTRAÇÃO
# ===========================================================================
if __name__ == "__main__":
    carro = Carro("ABC-1D23", "Onix", 2024, 150.0)
    moto = Moto("XYZ-9K88", "CG 160", 2023, 70.0, 160)
    caminhao = Caminhao("TRK-5E55", "Volvo FH", 2022, 600.0, 18000, 3)
    for v in (carro, moto, caminhao):
        print(v.exibir_ficha())

    pf = PessoaFisica("Maria Silva", "123.456.789-09", "(86) 99999-0000", date(1990, 5, 20))
    pj = PessoaJuridica("Transportes Norte LTDA", "12.345.678/0001-90", "(86) 3222-0000", "José Alves")
    print(pf.exibir_dados(), "| CPF válido:", pf.validar_documento())
    print(pj.exibir_dados(), "| CNPJ válido:", pj.validar_documento())

    print("\n--- Composição Contrato ◆ Condutor ---")
    hoje = date.today()
    contrato = Contrato(pf, carro, hoje, hoje + timedelta(days=5), "Pedro Santos", "12345678901")
    print(contrato.exibir_resumo())

    try:   # regra: veículo não pode estar em dois contratos ativos
        Contrato(pj, carro, hoje, hoje + timedelta(days=2), "Lucas Rocha", "10987654321")
    except ValueError as erro:
        print("Erro esperado:", erro)

    contrato.excluir()   # o condutor deixa de existir junto com o contrato
    print("Condutor após excluir contrato:", contrato.condutor)
    print("Carro disponível novamente:", carro.esta_disponivel())

    print("\n--- Composição Veiculo ◆ Manutencao ---")
    carro.registrar_manutencao(date(2026, 8, 10), "Troca de óleo", 250.0)
    carro.registrar_manutencao(date(2026, 9, 2), "Troca de pneus", 1600.0)
    for linha in carro.historico_manutencoes():
        print(" ", linha)
    print("Custo total:", carro.custo_total_manutencoes())
