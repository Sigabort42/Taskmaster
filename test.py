import smtplib    ## Importation du module
serveur = smtplib.SMTP('smtp.gmail.com', 587)    ## Connexion au serveur sortant (en précisant son nom et son port)
serveur.ehlo()
serveur.starttls()
serveur.ehlo()
#serveur.starttls()    ## Spécification de la sécurisation
serveur.login("allinplans@gmail.com", "Okokokok8")    ## Authentification
print("ici")
message = "Salut toi comment tu va ?"    ## Message à envoyer
serveur.sendmail("allinplans@gmail.com", "elbenkrizi@gmail.com", message)    ## Envoie du message
serveur.quit()    ## Déconnexion du serveur