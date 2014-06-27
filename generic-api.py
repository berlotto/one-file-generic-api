# /usr/bin/python
# -*- encoding: utf-8 -*-
#
# One file generic RESTFul API for databases
#
# ==============================================================================
# Configuration

DATABASE_URI = "mysql://root:root@localhost/database"
DEBUG = True

# ==============================================================================
from flask import Flask, jsonify
from sqlalchemy import or_, and_, desc
from sqlalchemy.sql import column
import sys
import sqlsoup

app = Flask(__name__)

app.debug = DEBUG

db = sqlsoup.SQLSoup(DATABASE_URI)

def format_return_data(return_from_table, table):
    linhas = []
    for linha in return_from_table:
        # colunas = [x for x in linha.__dict__ if not x.startswith('_')]
        dados_linha = dict( (name, getattr(linha, name)) for name in linha.__dict__ if not name.startswith('_'))
        linhas.append(dados_linha)
    return {table:linhas}


@app.route('/')
def index():
    data = {
        "message": "This is the index"
    }
    return jsonify(data)


@app.route('/<table>/')
def _table(table):
    try:
        _dados = db.entity(table).all()
        dados = format_return_data(_dados, table)
    except:
        dados = {
            'error_code':01,
            'error_msg':'Table %s does not exists' % table
        }
    return jsonify(dados)


@app.route('/<table>/orderby/<orderclause>/')
def _table_ordered(table, orderclause):
    """
    OrderClause is a formated string,
    field:[desc];field[desc];...
    """
    # import pdb; pdb.set_trace()
    orders = [ x.split(":") for x in orderclause.split(';') ]
    # try:
    tableobj = db.entity(table)
    for order in orders:
        if len(order) > 1 and order[1].lower() == "desc":
            tableobj=tableobj.order_by(desc( column(order[0]) ))
        else:
            tableobj=tableobj.order_by( column(order[0]) )
    _dados = tableobj.all()
    dados = format_return_data(_dados, table)
    # except:
    #     e = sys.exc_info()[0]
    #     dados = {
    #         'error_code': 01,
    #         'error_msg': str(e)
    #     }
    return jsonify(dados)


if __name__=="__main__":
    app.run(port=8888)

# - EOF
