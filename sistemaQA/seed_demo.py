"""
Script de seed — popula o banco com dados de exemplo para demonstração.
Execute: python seed_demo.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from modules.database import init_db
from modules import projects as p_mod, test_cases as tc_mod, scenarios as sc_mod, bugs as bug_mod

def main():
    init_db()

    # Projeto de exemplo
    pid = p_mod.create_project("Portal E-commerce", "Sistema de vendas online — Sprint 5")
    print(f"Projeto criado: id={pid}")

    # Suites
    s1 = tc_mod.create_suite(pid, "Login e Autenticação", "Testes de acesso ao sistema")
    s2 = tc_mod.create_suite(pid, "Checkout e Pagamento", "Fluxo de compra")
    s3 = tc_mod.create_suite(pid, "Catálogo de Produtos", "Listagem e busca")

    # Casos de teste — Login
    c1 = tc_mod.create_test_case(s1, "Login com credenciais válidas",
        "Verificar acesso com usuário e senha corretos",
        "Usuário cadastrado e ativo no sistema",
        "1. Acessar /login | 2. Inserir usuário | 3. Inserir senha | 4. Clicar em Entrar",
        "Redirecionamento para dashboard", "ALTA")
    tc_mod.update_test_case_status(c1, "PASSOU")

    c2 = tc_mod.create_test_case(s1, "Login com senha incorreta",
        "Verificar mensagem de erro ao inserir senha errada",
        "Usuário cadastrado no sistema",
        "1. Acessar /login | 2. Inserir usuário | 3. Inserir senha ERRADA | 4. Clicar Entrar",
        "Mensagem 'Credenciais inválidas' exibida", "ALTA")
    tc_mod.update_test_case_status(c2, "PASSOU")

    c3 = tc_mod.create_test_case(s1, "Login com usuário inexistente",
        "Verificar comportamento para usuário não cadastrado", "",
        "1. Inserir e-mail não cadastrado | 2. Clicar Entrar",
        "Mensagem de erro genérica sem revelar que o usuário não existe", "MÉDIA")
    tc_mod.update_test_case_status(c3, "PASSOU")

    c4 = tc_mod.create_test_case(s1, "Bloqueio após 5 tentativas falhas",
        "Conta deve ser bloqueada após 5 tentativas inválidas", "Usuário ativo sem bloqueio",
        "1. Fazer 5 logins com senha errada consecutivos",
        "Conta bloqueada e e-mail de aviso enviado", "CRÍTICA")
    tc_mod.update_test_case_status(c4, "FALHOU")

    # Casos de teste — Checkout
    c5 = tc_mod.create_test_case(s2, "Adicionar produto ao carrinho",
        "Verificar adição de item ao carrinho de compras", "Produto disponível em estoque",
        "1. Buscar produto | 2. Clicar 'Adicionar ao carrinho'",
        "Produto aparece no carrinho com quantidade 1", "ALTA")
    tc_mod.update_test_case_status(c5, "PASSOU")

    c6 = tc_mod.create_test_case(s2, "Finalizar compra com cartão de crédito",
        "Verificar pagamento com cartão válido", "Carrinho com ao menos 1 produto",
        "1. Ir para checkout | 2. Selecionar cartão | 3. Inserir dados | 4. Confirmar",
        "Pedido confirmado com número de rastreamento", "CRÍTICA")
    tc_mod.update_test_case_status(c6, "FALHOU")

    c7 = tc_mod.create_test_case(s2, "Aplicar cupom de desconto",
        "Verificar aplicação de cupom válido", "Cupom DESCONTO10 cadastrado e ativo",
        "1. Ir para carrinho | 2. Inserir cupom DESCONTO10 | 3. Clicar Aplicar",
        "Desconto de 10% aplicado ao total", "MÉDIA")
    tc_mod.update_test_case_status(c7, "PASSOU")

    c8 = tc_mod.create_test_case(s3, "Busca por nome de produto",
        "Verificar retorno de busca textual", "",
        "1. Acessar catálogo | 2. Digitar 'Notebook' no campo busca | 3. Pressionar Enter",
        "Lista de produtos contendo 'Notebook' exibida", "ALTA")
    tc_mod.update_test_case_status(c8, "BLOQUEADO")

    c9 = tc_mod.create_test_case(s3, "Filtrar por categoria",
        "Verificar filtragem por categoria", "",
        "1. Selecionar categoria 'Eletrônicos' | 2. Confirmar",
        "Somente produtos da categoria exibidos", "MÉDIA")
    # Não executado

    c10 = tc_mod.create_test_case(s3, "Ordenar por menor preço",
        "Verificar ordenação ascendente de preço", "",
        "1. Aplicar ordenação 'Menor Preço'",
        "Produtos listados em ordem crescente de valor", "BAIXA")
    # Não executado

    # Cenários Gherkin
    sc_mod.create_scenario(pid, "Usuário realiza login com sucesso",
        "que sou um usuário cadastrado com e-mail valido@email.com",
        "acesso a página de login e insiro as credenciais corretas",
        "sou redirecionado para o dashboard",
        "login, autenticação, smoke")
    sc_mod.update_scenario_status(1, "APROVADO")

    sc_mod.create_scenario(pid, "Carrinho persiste após logout e login",
        "que adicionei 3 produtos ao carrinho",
        "faço logout e entro novamente",
        "os 3 produtos ainda estão no meu carrinho",
        "carrinho, sessão, regressão")
    sc_mod.update_scenario_status(2, "REPROVADO")

    sc_mod.create_scenario(pid, "Cupom expirado não é aceito",
        "que tenho um cupom vencido",
        "tento aplicá-lo no checkout",
        "recebo a mensagem 'Cupom inválido ou expirado'",
        "cupom, validação")

    # Bugs
    bug_mod.create_bug(pid, "Bloqueio de conta não funciona após 5 tentativas",
        "Após inserir 5 senhas erradas consecutivas, o sistema não bloqueia a conta, "
        "permitindo tentativas ilimitadas de login.",
        "1. Tentar login com senha errada 5x | 2. Observar que nenhum bloqueio ocorre",
        "CRÍTICA", "produção", "Ana Souza", c4)

    bug_mod.create_bug(pid, "Falha ao finalizar compra com Visa",
        "O pagamento com cartão Visa retorna erro 500 na etapa de confirmação.",
        "1. Adicionar produto | 2. Ir para checkout | 3. Selecionar Visa | 4. Confirmar",
        "ALTA", "homologação", "Carlos Lima", c6)

    bug_mod.create_bug(pid, "Campo de busca não funciona no mobile",
        "Em dispositivos móveis, o campo de busca do catálogo não aceita digitação.",
        "1. Acessar catálogo via iPhone | 2. Tocar no campo busca | 3. Tentar digitar",
        "ALTA", "iOS 17 / Safari", "Maria Oliveira")
    bug_mod.update_bug_status(3, "EM ANÁLISE")

    bug_mod.create_bug(pid, "Preço exibido sem formatação de moeda",
        "O preço de alguns produtos aparece sem a formatação R$ em certas páginas.",
        "1. Acessar página de detalhes do produto ID 142",
        "BAIXA", "staging", "João Pereira")
    bug_mod.update_bug_status(4, "CORRIGIDO")

    print("Dados de demonstração inseridos com sucesso!")

if __name__ == "__main__":
    main()
