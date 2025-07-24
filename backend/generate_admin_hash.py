#!/usr/bin/env python3
"""
Script pour générer le hash bcrypt du mot de passe "admin"
"""

from passlib.context import CryptContext

# Créer le contexte de hachage
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Générer le hash pour "admin"
password = "admin"
hashed_password = pwd_context.hash(password)

print(f"Mot de passe: {password}")
print(f"Hash bcrypt: {hashed_password}")

# Vérifier que le hash fonctionne
is_valid = pwd_context.verify(password, hashed_password)
print(f"Vérification: {is_valid}") 