from decimal import Decimal

from flask import Flask, abort, render_template,request
from mysql.connector import Error

from conexao import consultar, consultar_um

app = Flask(__name__)

@app.route("/")
def inicio():
    return render_template("index.html")

@app.route("/sobre")
def sobre():
    return render_template("sobre.html")

@app.route("/produtos")
def produtos():
    busca = request.args.get("busca", "").strip()
    sql = """
        select p.id_produto as ID,
        p.nome_produto as Produto,
        c.categoria,
        p.preco_unit as preco
        from produtos as p
        inner join categorias as c
        on c.id_categoria = p.id_categoria
        where p.nome_produto like %s
        order by p.nome_produto
        """
    dados = consultar(sql, (f"%{busca}%",))
    return render_template("tabela.html", titulo="Produtos", dados=dados, busca=busca)

@app.errorhandler(Error)
def erro_banco(erro):
    """Qualquer erro de banco fora de um formulário cai aqui."""
    app.logger.error("Falha MySQL %s", erro.errno)
    mensagem = "Falha ao acessar o banco. Confira o .env e se o MySQL está ligado."
    return render_template("erro.html", mensagem=mensagem), 503

@app.route("/categorias")
def categorias():
    sql = "select ID_categoria as ID, categoria from categorias order by categoria"
    return render_template("tabela.html", titulo="categorias", dados=consultar(sql))

@app.route("/locais")
def locais():
    sql = """
    select id_local as id,
    cidade, estado, regiao
    from locais 
    order by estado, cidade
    """
    return render_template("tabela.html", titulo="locais", dados=consultar(sql))

@app.route("/cliente")
def clientes():
    busca = request.args.get("busca", "").strip()
    sql = """
    select id_clientes as id,
    nome,
    sobrenome,
    email
    from clientes
    where concat_ws(" ",nome,sobrenome) like %s
    order by nome, sobrenome
    """
    dados = consultar(sql, (f"%{busca}%",))
    return render_template("tabela.html", titulo="clientes", dados=dados, busca=busca, vazio="Nenhum cliente com esse nome.")

@app.route("/lojas")
def lojas():
    sql = """
    select l.id_loja as id,
    l.loja,
    loc.cidade,
    loc.estado
    from lojas as l
    inner join locais as loc
    on loc.id_local = l.id_local
    order by l.loja
    """
    return render_template("tabela.html", titulo="lojas", dados=consultar(sql))

@app.route("/vendedor")
def vendedores():
    sql = """
    select v.id_vendedor as id,
    v.nome,
    v.email,
    l.loja
    from vendedores as v
    inner join lojas as l
    on l.id_loja = v.id_loja
    order by v.nome
    """
    return render_template("tabela.html", titulo="Vendedores", dados=consultor(sql), vazio="Nenhum vendedor cadastro.")

@app.route("/pedidos")
def pedidos():
    sql = """
    select p.id_pedido as id,
    p.data_pedido as data,
    concat_ws(" ",c.nome, c.sobrenome) as cliente,
    l.loja,
    v.nome as vendedor,
    s.descricao as status,
    p.valor_total as total,
    p.origem_registro as origem
    from pedidos as p
    inner join clientes as c
    on c.id_cliente = P.ID_cliente
    inner join lojas as l
    on l.id_loja = p.id_loja
    inner join status_pedido as s
    on s.ID_status = p.id_status
    left join vendedores as v
    on v.id_vendedor = p.id_vendedor
    order by p.id_pedido desc
    limit 100
    """
    return render_template("tabela.html", titulo="pedidos (100 mais recentes)", dados=consultar(sql), detalhe="pedido_detalhe")

@app.route("/pedidos/<int:ident>")
def pedido_detalhe(ident):
    pedido = consultar_um("""
                          select p.id_pedido,
                          p.valor_total,
                          p.origem_registro,
                          concat_ws(" ",c.nome,c.sobrenome) as cliente,
                          l.loja,
                          v.nome as vendedor,
                          s.descricao as status""")