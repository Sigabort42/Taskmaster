# TaskMaster
Taskmaster est un processus de job control à part entière. Il se rapproche de supervisor.

Pour rester dans quelque chose d’assez simple, le processus ne  tourne pas en tant que root.

Il sera executé via le terminal et fera son travail pendant qu’il donnera l’accès au shell à l’utilisateur.

**Commandes Disponibles**

* **?** or **help**   [right]Afficher l'aide et les commandes disponibles[/right]
* **start** *name* | *all*   [right]Demarrer un programme ou tout les programmes stoppe[/right]
* **stop** *name* **|** *all* [right]Stopper un programme ou tout les programmes demarre[/right]
* **restart** *name* **|** *all* [right]Redemarrer un programme ou tout les programmes stoppe[/right]
* **reload** [right]Recharger le fichiers de configuration et relancer les processus qui en ont besoin[/right]
  * modifier la commande
  * modifier l'umask
  * modifier le directory
  * modifier les stdout, stderr
  * modifier l'environnement