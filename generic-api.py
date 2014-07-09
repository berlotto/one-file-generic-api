# /usr/bin/python
# -*- encoding: utf-8 -*-
#
# One file generic RESTFul API for databases
#
# ==============================================================================
# Configuration

DATABASE_URI = "mysql://root:root@localhost/gabdigprod?charset=utf8"
DEBUG = True

# ==============================================================================
from flask import Flask, jsonify, url_for
from sqlalchemy import or_, and_, desc
from sqlalchemy.sql import column
import sys
import sqlsoup
import urllib

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


@app.route("/site-map/")
def list_routes():
    """
    Return all endpoints of this script.
    Tks to: http://stackoverflow.com/a/22651263
    """
    output = []
    for rule in app.url_map.iter_rules():
        methods = ','.join(rule.methods)
        line = urllib.unquote("{:50s} {:20s} {}".format(rule.endpoint, methods, rule))
        output.append(line)

    return jsonify(endpoints=sorted(output))


@app.route('/all_tables/', defaults={"filter":None})
@app.route('/all_tables/<string:filter>/')
def _show_tables(filter):
    """
    List all tables in database.
    filter: String , part of the name of tables to list
    """
    pointer = db.execute('show tables') #<- This is for MySQL, change for others
    tables = []
    for t in pointer:
        if (filter and t[0].find(filter) >= 0) or not filter:
            tables.append(t[0])
    return jsonify(tables=tables)


@app.route('/<table>/', defaults={'limit':None})
@app.route('/<table>/limit/<int:limit>/')
def _table(table, limit):
    """
    List all registers of the table
    table: the name of the table
    limit: the limit of returned registers
    """
    try:
        if limit:
            _dados = db.entity(table).limit(limit).all()
        else:
            _dados = db.entity(table).all()
        dados = format_return_data(_dados, table)
    except:
        dados = {
            'error_code':01,
            'error_msg':'Table %s does not exists' % table
        }
    return jsonify(dados)


@app.route('/<table>/filter/<filter>/')
def _table_filter(table):
    """
    List all registers of the table
    """
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
