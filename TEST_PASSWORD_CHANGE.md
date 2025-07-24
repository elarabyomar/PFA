# Test de la Fonctionnalité de Changement de Mot de Passe

## 🧪 **Scénarios de test**

### **Test 1 : Connexion avec mot de passe "admin"**

1. **Redémarrez l'application** :
   ```bash
   docker-compose down
   docker-compose up -d
   ```

2. **Connectez-vous avec** :
   - Email : `admin@gmail.com`
   - Mot de passe : `admin`

3. **Résultat attendu** :
   - ✅ Connexion réussie
   - ✅ Redirection automatique vers `/change-password`
   - ✅ Avertissement visible dans le menu et la page d'accueil

### **Test 2 : Connexion avec date de naissance**

1. **Connectez-vous avec** :
   - Email : `admin@gmail.com`
   - Mot de passe : `2003-11-25` (date de naissance)

2. **Résultat attendu** :
   - ✅ Connexion réussie
   - ✅ Redirection automatique vers `/change-password`

### **Test 3 : Vérification des éléments visuels**

Après connexion avec mot de passe par défaut, vérifiez :

1. **Menu latéral** :
   - ✅ Lien "Changer le mot de passe" visible (en orange)
   - ✅ Chip "Mot de passe à changer" sous le nom d'utilisateur

2. **Page d'accueil** :
   - ✅ Alert d'avertissement en haut
   - ✅ Chip "Mot de passe à changer" dans le profil
   - ✅ Bouton "Changer maintenant" fonctionnel

3. **Menu utilisateur** (icône en haut à droite) :
   - ✅ Option "Changer le mot de passe" visible

### **Test 4 : Changement de mot de passe**

1. **Accédez à la page de changement** :
   - Cliquez sur "Changer le mot de passe" dans le menu

2. **Testez la validation** :
   - ❌ Mot de passe faible (doit être rejeté)
   - ✅ Mot de passe conforme (doit être accepté)

3. **Exemple de mot de passe valide** :
   ```
   Mot de passe actuel : admin
   Nouveau mot de passe : CrystalAssur2024!
   Confirmation : CrystalAssur2024!
   ```

4. **Résultat attendu** :
   - ✅ Message de succès
   - ✅ Redirection vers `/home`
   - ✅ Avertissements disparus
   - ✅ Lien "Changer le mot de passe" disparu du menu

### **Test 5 : Connexion après changement**

1. **Déconnectez-vous** et reconnectez-vous avec le nouveau mot de passe

2. **Résultat attendu** :
   - ✅ Connexion réussie
   - ✅ Redirection vers `/home` (pas `/change-password`)
   - ✅ Aucun avertissement visible

## 🔧 **Dépannage**

### **Si la redirection ne fonctionne pas :**

1. **Vérifiez les logs du backend** :
   ```bash
   docker logs auth-backend-1
   ```

2. **Vérifiez la base de données** :
   ```bash
   docker exec -it auth-backend-1 psql -U postgres -d auth_db -c "SELECT email, password_changed FROM users WHERE email = 'admin@gmail.com';"
   ```

3. **Vérifiez la console du navigateur** pour les erreurs JavaScript

### **Si le mot de passe "admin" ne fonctionne pas :**

1. **Vérifiez le hash dans la base** :
   ```bash
   docker exec -it auth-backend-1 psql -U postgres -d auth_db -c "SELECT email, password FROM users WHERE email = 'admin@gmail.com';"
   ```

2. **Le hash devrait être** : `$2b$12$CKQs0OA0wWxhglZFzVU/MeXxeTsOGlSlVOeq1ci51n0XPGjGiUPy.`

## 📋 **Checklist de validation**

- [ ] Connexion avec "admin" → redirection vers `/change-password`
- [ ] Connexion avec date de naissance → redirection vers `/change-password`
- [ ] Avertissements visibles dans l'interface
- [ ] Validation du mot de passe fonctionnelle
- [ ] Changement de mot de passe réussi
- [ ] Connexion avec nouveau mot de passe → pas de redirection
- [ ] Avertissements disparus après changement

## 🎯 **Résultat final**

Après tous les tests, l'utilisateur admin devrait :
1. Être forcé de changer son mot de passe par défaut
2. Voir des avertissements clairs dans l'interface
3. Pouvoir changer son mot de passe avec validation stricte
4. Ne plus voir d'avertissements après le changement 