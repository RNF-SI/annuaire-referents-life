from crypt import methods
from flask import Flask, request, redirect, url_for, render_template, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_mail import Mail, Message
from config import Config
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow

app = Flask(__name__)
app.config.from_object(Config)
mail = Mail()

db = SQLAlchemy(app)
ma = Marshmallow(app)

migrate = Migrate(app, db)

mail.init_app(app)

class Annuaire(db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    prenom = db.Column(db.String(100))
    nom = db.Column(db.String(100))
    email = db.Column(db.String(100))
    telephone = db.Column(db.String(10))
    fonction = db.Column(db.String(255))
    site = db.Column(db.String(255))
    structure = db.Column(db.String(255))
    # region = db.Column(db.String(100))
    # departement = db.Column(db.String(100))
    # adresse = db.Column(db.String(100))
    # commune = db.Column(db.String(100))
    # code_postal = db.Column(db.String(5))
    # telephone_port = db.Column(db.String(10))
    # reseau = db.Column(db.String(100))
    lat = db.Column(db.Float)
    long = db.Column(db.Float)
    # sites = db.relationship('Site', backref='annuaire', lazy=True)
    # expertises = db.relationship('Expertise', backref='annuaire', lazy=True)
    # created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    # active = db.Column(db.Boolean, server_default=u'false')
    activites = db.relationship("Activite", back_populates='structure')

class Activite(db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    titre = db.Column(db.String(255))
    enligne = db.Column(db.Boolean)
    site_web = db.Column(db.String(255))
    date = db.Column(db.DateTime)
    adresse = db.Column(db.String(255))
    description = db.Column(db.Text)
    inscription = db.Column(db.Boolean)
    gratuit = db.Column(db.Boolean)
    lien_inscription = db.Column(db.String(255))
    annuaire_id = db.Column(db.Integer, db.ForeignKey('annuaire.id'),
        nullable=False)
    structure = db.relationship("Annuaire", back_populates = 'activites')

@app.route("/")
def index():
    contacts = Annuaire.query.all()
    activites = Activite.query.all()
    return render_template('index.html', contacts=contacts, activites=activites)

@app.route('/ajout-site', methods=['GET', 'POST'])
def ajout_site():
    if request.method == 'POST':
        prenom = request.form.get('prenom') or None
        nom = request.form.get('nom') or None
        # region = request.form.get('region')
        # departement = request.form.get('departement')
        # adresse = request.form.get('adresse') or None
        # commune = request.form.get('commune') or None
        # code_postal = request.form.get('code_postal') or None
        email = request.form.get('email') or None
        telephone = request.form.get('telephone') or None
        # telephone_port = request.form.get('telephone_port') or None
        # reseau = request.form.get('reseau')
        structure = request.form.get('structure') or None
        fonction = request.form.get('fonction') or None
        site = request.form.get('site') or None
        lat = request.form.get('lat') or None
        long = request.form.get('long') or None

        annuaire = Annuaire(prenom = prenom, nom = nom, lat = lat, long = long, email = email, telephone = telephone, structure = structure, fonction = fonction, site=site)
        db.session.add(annuaire)

        msg = Message("Ajout d'un référent au MOOC", sender = 'si@rnfrance.org',
                recipients = ['si@rnfrance.org'],
                body= "Un référent a été ajouté au MOOC"
        )
        mail.send(msg)
        db.session.commit()

        contact = Annuaire.query.filter_by(prenom = prenom, nom = nom, email = email).first()

        
        if request.form.get('type_ajout') == 'activite' :
            flash(u'Nouveau référent correctement ajouté. Vous pouvez maintenant ajouter une activité', 'success')
            return redirect(url_for('ajout_activite', id=contact.id))
        else :            
            flash(u'Nouveau référent correctement ajouté.', 'success')
            return render_template('index.html')
    else:
        return render_template('ajout_site.html')

@app.route('/ajout-activite/<id>', methods=['GET', 'POST'])
def ajout_activite(id):

    contact = Annuaire.query.filter_by(id=id).first()
    
    if request.method == 'POST':

        print(request.form.get('inscription'))
        print(request.form.get('gratuit'))

        titre = request.form.get('titre') or None
        type_activite = request.form.get('type_activite') or None
        if type_activite == 'online' :
            enligne = True
        elif type_activite == 'physique' :
            enligne = False
        site_web = request.form.get('site_web') or None
        date = request.form.get('date') or None
        adresse = request.form.get('adresse') or None
        description = request.form.get('description') or None
        inscription = request.form.get('inscription') or None
        if inscription == "on" :
            inscription = True
        else :
            inscription = False
        gratuit = request.form.get('gratuit') or None
        if gratuit == "on" :
            gratuit = True
        else : 
            gratuit = False
        lien_inscription = request.form.get('lien_inscription') or None

        activite = Activite(titre=titre,enligne=enligne,site_web=site_web,date=date,adresse=adresse,description=description,inscription=inscription,gratuit=gratuit,lien_inscription=lien_inscription, annuaire_id=contact.id)

        db.session.add(activite)

        msg = Message("Ajout d'une activité au MOOC", sender = 'si@rnfrance.org',
                    recipients = ['si@rnfrance.org'],
                    body= "Une activité a été ajouté au MOOC pour la structure %s" % contact.structure
            )
        mail.send(msg)

        db.session.commit()

        if request.form.get('autre_activite') == 'on' :
            flash(u'Nouvelle activité correctement ajoutée. Vous pouvez en ajouter une autre.', 'success')
            return redirect(url_for('ajout_activite', id=contact.id))
        else :            
            flash(u'Nouvelle activité correctement ajoutée.', 'success')
            return render_template('index.html')
    else:

        return render_template('ajout_activite.html', contact=contact)
    
if __name__ == '__main__':
      app.run(host='0.0.0.0', port=5020)
