# Project Brain

## Règles Métier Validées

### Authentication & Login [US_001]
- **Interface UI** :
  - Titre colonne gauche : "Customer Login".
  - Bouton : "LOG IN" (Orange, Majuscules).
  - Liens requis : "Forgot login info?" et "Register".
- **Logique** :
  - Username sensible à la casse.
  - **Messages d'erreur stricts** :
    - "The username and password could not be verified."
    - "Please enter a username and password."

### Inscription & Création de Compte [SCRUM-189]

| Phase | Règles UI & Métier |
| :--- | :--- |
| **Structure & UI** | • **Titre Page** : "Signing up is easy!".<br>• **Ordre Formulaire (Strict 11 Champs)** : 1. First Name, 2. Last Name, 3. Address, 4. City, 5. State, 6. Zip Code, 7. Phone #, 8. SSN, 9. Username, 10. Password, 11. Confirm. |
| **Validation & Erreurs** | • **Champs Obligatoires** : Tous sauf "Phone #" (seul champ optionnel).<br>• **Style Erreur** : Texte **rouge**, affichage **inline** (à droite du champ).<br>• **Syntaxe Erreurs** :<br>&nbsp;&nbsp;- Standard : `[Field name] is required.` (Ex: "First name is required.")<br>&nbsp;&nbsp;- Exception Confirm : `Password confirmation is required.`<br>&nbsp;&nbsp;- Unicité : `This username already exists.` (si doublon).<br>&nbsp;&nbsp;- Concordance : `Passwords did not match.` |
| **Sécurité & Formats** | • **Sécurité UX** : Les champs 'Password' et 'Confirm' sont **systématiquement vidés** dès qu'une erreur de validation (notamment la non-concordance) survient.<br>• **Flexibilité des données** : Pas de contrainte de format pour SSN, Zip Code (texte libre) et Password. |
| **Succès & Post-Inscription** | • **Auto-login** : Connexion automatique immédiate après validation.<br>• **Message de confirmation** : "Your account was created successfully. You are now logged in."<br>• **Bandeau de bienvenue** : Affiche "Welcome [First Name] [Last Name]". |

### Dashboard & Navigation
- **Barre Latérale Gauche** :
  - Message : "Welcome [First Name] [Last Name]" (Format validé post-inscription).
  - Menu : "Account Services" [US_001].
  - **Liens Services** :
    - "Open New Account" (Visible uniquement si connecté) [SCRUM-700].
    - "Update Contact Info" (Mise à jour profil) [SCRUM-303].
- **Tableau de Synthèse** [US_001] :
  - Colonnes : Account, Balance, Available.
  - Présence obligatoire de la ligne "Total" et de la note de bas de page.

### Opérations : Ouverture de Compte [SCRUM-700]

| Phase | Règles UI & Métier |
| :--- | :--- |
| **Accès & Formulaire** | • **Accès** : Menu latéral "Open New Account".<br>• **Saisie** : Type de compte (`Checking`, `Savings`) et Compte Source.<br>• **Montant** : Aucune saisie de montant initial.<br>• **Action** : Bouton libellé "Open New Account". |
| **Confirmation (Succès)** | • **Titre** : "Account Opened!"<br>• **Message** : "Congratulations, your account is now open."<br>• **Redirection** : Affichage de "Your new account number: {Numéro}" (Lien cliquable).<br>• **Navigation** : Aucun bouton retour. |

### Opérations : Mise à jour du Profil [SCRUM-303]

| Phase | Règles UI & Métier |
| :--- | :--- |
| **Accès & Initialisation** | • **Flux** : Menu Gauche "Update Contact Info".<br>• **Pré-remplissage** : Obligatoire au chargement avec les données actuelles. |
| **Formulaire (Structure)** | • **Ordre Strict (7 Champs)** : 1. First Name, 2. Last Name, 3. Address, 4. City, 5. State, 6. Zip Code, 7. Phone #.<br>• **Exclusions** : Champ "Email" strictement invisible.<br>• **Contraintes** : Max 255 caractères par champ. |
| **Validation & Erreurs** | • **Champs Obligatoires** : Tous sauf "Phone #".<br>• **Affichage Erreur** : Inline à droite, texte rouge.<br>• **Syntaxe** : `[Nom du champ] is required.` |
| **Flux de Succès** | • **Confirmation** : Titre "Profile Updated" et message statique de succès.<br>• **Qualité (QA)** : Test de persistance obligatoire (Logout/Login pour valider DB). |

## Jeux de Données Préférés

### Identifiants Utilisateurs
| Username | Password | Firstname | Lastname | Notes |
| :--- | :--- | :--- | :--- | :--- |
| `john` | `demo` | Jhon | Smith | Utilisateur standard existant |

### Données de Test Validées (JDD)
| Fonctionnalité | Scénario | Valeurs / Exemples Validés |
| :--- | :--- | :--- |
| **Register** [SCRUM-189] | Happy Path (John) | `firstName="John"`, `phone="555-0199"`, `ssn="999-00-01"` |
| **Register** [SCRUM-189] | Happy Path (Minimal) | `phone=""` (Champ optionnel, succès attendu) |
| **Register** [SCRUM-189] | Erreur Unicité | `existing_user="john"` -> "This username already exists." |
| **Register** [SCRUM-189] | Erreur Concordance | Pass: `pass1` / Confirm: `pass2` -> "Passwords did not match." (+ vidage champs) |
| **Register** [SCRUM-189] | Erreur Mandatory | Champ "Confirm" vide -> "Password confirmation is required." |
| **Register** [SCRUM-189] | Erreur Mandatory | Autre champ vide -> "[Field] is required." |
| **Update Profile** [SCRUM-303] | Validation Persistance | First Name: `Jhonnn` (Utiliser 3 'n' pour vérification visuelle) |
| **Update Profile** [SCRUM-303] | Cas Limites | Zip Code: `TextZip` (Alphanumérique accepté) |

## Cartographie des Modèles LLM (Architecture)

| Composant | Modèle | Rôle / Justification |
| :--- | :--- | :--- |
| **Agents CrewAI** | `gemini-3-pro-preview` | Raisonnement stratégique. (Quota: 25 RPM) |
| **Knowledge (Update)** | `gemini-3-pro-preview` | Synthèse Markdown. (Quota: 25 RPM) |
| **Knowledge (Query)** | `gemini-3-flash-preview` | Lecture rapide. (Quota: 1000 RPM) |
| **Vision & Vidéo** | `gemini-3-flash-preview` | Identification UI et analyse de flux. (Quota: 1000 RPM) |

## Directives Techniques (SDET)

### Sélecteurs Playwright (Stabilité)
- **Scoping Obligatoire** : Préfixer les locateurs par `#rightPanel` (Strict Mode) pour éviter les éléments cachés du menu.
  - *Exemple* : `page.locator('#rightPanel .title')`
- **Visibilité** : Filtrer par `.filter({ visible: true })` pour les titres génériques.

### Reporting & Validation
- **Objectif** : 100% de réussite sur les 10 scénarios critiques.
- **Confirmation** : L'agent doit confirmer le score de 100% et fournir le lien local vers le rapport Playwright avant de clore la session.

> [!NOTE]
> Les configurations sont centralisées dans `src/config.py` (facilite la maintenance globale).