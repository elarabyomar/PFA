from pydantic import BaseModel, Field
 
class AdminPasswordChangeDTO(BaseModel):
    """DTO pour changer le mot de passe admin par défaut"""
    current_admin_password: str = Field(..., description="Mot de passe admin actuel")
    new_admin_password: str = Field(..., min_length=6, description="Nouveau mot de passe admin")
    confirm_new_password: str = Field(..., description="Confirmation du nouveau mot de passe") 