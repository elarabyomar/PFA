# Fonctionnalité de Changement de Mot de Passe Obligatoire

## Vue d'ensemble

Cette fonctionnalité permet de forcer les utilisateurs à changer leur mot de passe par défaut (date de naissance) lors de leur première connexion. L'utilisateur est automatiquement redirigé vers une page de changement de mot de passe avec des règles de sécurité strictes.

## Fonctionnalités

### Backend

1. **Nouveau champ dans le modèle User** :
   - `password_changed` : Boolean pour suivre si l'utilisateur a changé son mot de passe

2. **Nouveaux endpoints** :
   - `POST /auth/change-password` : Pour changer le mot de passe
   - Modification de `POST /auth/login` : Détecte si le mot de passe est la date de naissance

3. **Logique de détection** :
   - Compare le mot de passe saisi avec la date de naissance au format YYYY-MM-DD
   - Retourne `requires_password_change: true` si c'est le mot de passe par défaut

### Frontend

1. **Nouvelle page** : `ChangePasswordPage.js`
   - Design moderne inspiré de l'image fournie
   - Validation en temps réel du mot de passe
   - Indicateur de force du mot de passe
   - Règles de sécurité affichées

2. **Règles de sécurité strictes** :
   - Au moins 12 caractères
   - 3 catégories minimum (majuscules, minuscules, chiffres, spéciaux)
   - Pas plus de 2 caractères identiques consécutifs
   - Pas de mots du dictionnaire commun
   - Pas de séquences communes (123, abc, etc.)

3. **Gestion du contexte** :
   - Nouveau state `requiresPasswordChange`
   - Fonction `passwordChanged()` pour mettre à jour le contexte
   - Redirection automatique vers `/change-password` si nécessaire

## Installation et Configuration

### 1. Mise à jour de la base de données

Exécutez le script SQL pour ajouter le nouveau champ :

```sql
-- Ajouter la colonne password_changed
ALTER TABLE users ADD COLUMN IF NOT EXISTS password_changed BOOLEAN DEFAULT FALSE;

-- Marquer l'admin comme devant changer son mot de passe
UPDATE users SET password_changed = FALSE WHERE email = 'admin@gmail.com';
```

### 2. Redémarrage des services

```bash
# Backend
cd backend
docker-compose down
docker-compose up -d

# Frontend
cd frontend
npm install
npm start
```

## Utilisation

### Scénario typique

1. **Première connexion de l'admin** :
   - L'admin se connecte avec `admin@gmail.com` et sa date de naissance
   - Le système détecte que c'est le mot de passe par défaut
   - L'utilisateur est automatiquement redirigé vers `/change-password`

2. **Page de changement de mot de passe** :
   - L'utilisateur doit saisir son mot de passe actuel
   - Il choisit un nouveau mot de passe conforme aux règles
   - L'interface affiche la force du mot de passe en temps réel
   - Validation côté client et serveur

3. **Après le changement** :
   - Le mot de passe est mis à jour en base
   - Le champ `password_changed` passe à `true`
   - L'utilisateur est redirigé vers `/home`

### Règles de validation

Le mot de passe doit respecter toutes ces règles :

- ✅ **Longueur** : Au moins 12 caractères
- ✅ **Complexité** : 3 catégories minimum (majuscules, minuscules, chiffres, spéciaux)
- ✅ **Sécurité** : Pas de caractères consécutifs identiques
- ✅ **Dictionnaire** : Pas de mots communs
- ✅ **Séquences** : Pas de séquences communes (123, abc, etc.)

## Sécurité

### Mesures implémentées

1. **Validation côté client et serveur**
2. **Hachage bcrypt** pour les mots de passe
3. **JWT** pour l'authentification
4. **Redirection forcée** si changement requis
5. **Règles de sécurité strictes**

### Protection contre les attaques

- ✅ Validation des entrées
- ✅ Protection CSRF (via JWT)
- ✅ Hachage sécurisé des mots de passe
- ✅ Expiration des tokens
- ✅ Validation des règles de complexité

## Fichiers modifiés/créés

### Backend
- `model/user.py` : Ajout du champ `password_changed`
- `dto/user_dto.py` : Nouveau DTO `ChangePasswordDTO`
- `service/auth_service.py` : Fonctions de détection et changement
- `controller/auth_controller.py` : Nouveaux endpoints
- `config/database/update_password_changed.sql` : Script de migration

### Frontend
- `pages/auth/ChangePasswordPage.js` : Nouvelle page (créée)
- `components/auth/PasswordChangeRoute.js` : Route protégée (créée)
- `services/authService.js` : Fonction `changePassword`
- `context/AuthContext.js` : Gestion du state `requiresPasswordChange`
- `pages/auth/LoginPage.js` : Redirection vers changement de mot de passe
- `App.js` : Nouvelle route `/change-password`

## Tests

### Test de la fonctionnalité

1. **Connexion avec mot de passe par défaut** :
   ```bash
   # Utilisez la date de naissance de l'admin
   Email: admin@gmail.com
   Password: 1990-01-01 (ou la date de naissance configurée)
   ```

2. **Vérification de la redirection** :
   - L'utilisateur doit être redirigé vers `/change-password`
   - La page doit afficher le formulaire de changement

3. **Test de validation** :
   - Essayez des mots de passe faibles (doivent être rejetés)
   - Testez un mot de passe conforme (doit être accepté)

4. **Vérification finale** :
   - Après le changement, l'utilisateur doit être redirigé vers `/home`
   - Les connexions suivantes ne doivent plus demander de changement

## Dépannage

### Problèmes courants

1. **Erreur de migration** :
   ```bash
   # Vérifiez que le script SQL a été exécuté
   docker exec -it auth-backend-1 psql -U postgres -d auth_db -c "SELECT column_name FROM information_schema.columns WHERE table_name = 'users';"
   ```

2. **Redirection en boucle** :
   - Vérifiez que `requiresPasswordChange` est correctement mis à jour
   - Contrôlez les logs du navigateur pour les erreurs

3. **Validation qui ne fonctionne pas** :
   - Vérifiez que les règles de validation sont respectées
   - Contrôlez la force du mot de passe (doit être ≥ 80%)

## Support

Pour toute question ou problème avec cette fonctionnalité, consultez :
- Les logs du backend dans Docker
- La console du navigateur pour les erreurs frontend
- La documentation des dépendances utilisées 