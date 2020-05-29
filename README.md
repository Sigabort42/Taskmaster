# TaskMaster
Taskmaster est un processus de job control à part entière. Il se rapproche de supervisor.

Pour rester dans quelque chose d’assez simple, le processus ne  tourne pas en tant que root.

Il sera executé via le terminal et fera son travail pendant qu’il donnera l’accès au shell à l’utilisateur.

**Commandes Disponibles**

* `TaskMaster $>?` or `TaskMaster $>help` **Afficher l'aide et les commandes disponibles**
* `TaskMaster $>status`  **Voir le details des processus lancé**
* `TaskMaster $>info` `name` **Toutes les informations de configuration du processus {*name*}**
* `TaskMaster $>start` `name|all` **Demarrer un programme ou tout les programmes stoppé**
* `TaskMaster $>stop` `name|all` **Stopper un programme ou tout les programmes demarré**
* `TaskMaster $>restart` `name|all` **Redemarrer un programme ou tout les programmes stoppé**
* `TaskMaster $>reload` **Recharger le fichiers de configuration et relancer les processus qui en ont besoin**
  * modifier la commande
  * modifier l'umask
  * modifier le directory
  * modifier les stdout, stderr
  * modifier l'environnement