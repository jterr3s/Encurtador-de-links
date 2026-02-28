from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
import random
import string

app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://usuario:senha@localhost:5432/postgres'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class LinksRedi(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    linkOri = db.Column(db.String(255), nullable=False)
    novoLink = db.Column(db.String(120), unique=True)
    acessos = db.Column(db.Integer, default=0)


def gerarLink():

    caracteres = string.ascii_letters + string.digits
    
    return ''.join(random.choice(caracteres) for _ in range(6))


def initDb():
    with app.app_context():

        db.create_all()
        print("Banco de dados inicializado.")


@app.route("/")
def homepage():

    return render_template("homepage.html")

@app.route("/encurtar", methods=['POST'])
def encurtar():
    link_original = request.form.get('url_longa')
    
    if not link_original:
        return "URL inválida", 400
        
    tentativas = 0
    novo_link_curto = ""
    
    while True:
        codigo_proposto = gerarLink()
        link_existente = LinksRedi.query.filter_by(novoLink=codigo_proposto).first()
        
        if not link_existente:
            novo_link_curto = codigo_proposto
            break
        
        tentativas += 1
        if tentativas > 100:
            return "Erro ao gerar link único", 500
    

    novo_registro = LinksRedi(linkOri=link_original, novoLink=novo_link_curto)
    db.session.add(novo_registro)
    db.session.commit()

    link_completo = request.host_url + novo_link_curto
    
    return render_template('homepage.html', link_pronto=link_completo)

@app.route('/<codigo_recebido>')
def redirecionar(codigo_recebido):
    link_no_banco = LinksRedi.query.filter_by(novoLink=codigo_recebido).first()

    if link_no_banco:
        link_no_banco.acessos += 1
        db.session.commit()

        destino = link_no_banco.linkOri
        if not destino.startswith(('http://', 'https://')):
            destino = 'http://' + destino
            
        return redirect(destino)
    
    return "Link não encontrado", 404

if __name__ == "__main__":
    initDb()
    app.run(debug=True)