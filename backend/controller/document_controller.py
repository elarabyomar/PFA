from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import logging
import os
from service.document_service import DocumentService
from dto.document_dto import DocumentResponse, AdherentResponse, ClientCreateWithDocuments
from config.database.database import get_session
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Log when this module is imported
logger.info("🔍 Document controller module imported")
logger.info(f"🔍 Logger name: {__name__}")

router = APIRouter(prefix="/api/documents", tags=["documents"])

# Log router creation
logger.info(f"🔍 Creating document router with prefix: {router.prefix}")
logger.info(f"🔍 Document router tags: {router.tags}")

@router.post("/clients", response_model=dict)
async def create_client_with_documents(
    client_data: ClientCreateWithDocuments,
    session: AsyncSession = Depends(get_session)
):
    """Create a new client with documents and adherents"""
    logger.info("🔍 create_client_with_documents endpoint called")
    logger.info(f"📥 Received client data: {client_data}")
    logger.info(f"📥 Client data type: {type(client_data)}")
    logger.info(f"📥 Client data dict: {client_data.dict()}")
    
    # Debug SOCIETE fields specifically
    if hasattr(client_data, 'typeClient') and client_data.typeClient == 'SOCIETE':
        logger.info(f"🔍 SOCIETE client detected, checking fields:")
        logger.info(f"   nom: {getattr(client_data, 'nom', 'NOT_FOUND')}")
        logger.info(f"   formeJuridique: {getattr(client_data, 'formeJuridique', 'NOT_FOUND')}")
        logger.info(f"   capital: {getattr(client_data, 'capital', 'NOT_FOUND')}")
        logger.info(f"   registreCom: {getattr(client_data, 'registreCom', 'NOT_FOUND')}")
        logger.info(f"   taxePro: {getattr(client_data, 'taxePro', 'NOT_FOUND')}")
        logger.info(f"   idFiscal: {getattr(client_data, 'idFiscal', 'NOT_FOUND')}")
        logger.info(f"   CNSS: {getattr(client_data, 'CNSS', 'NOT_FOUND')}")
        logger.info(f"   ICE: {getattr(client_data, 'ICE', 'NOT_FOUND')}")
        logger.info(f"   siteWeb: {getattr(client_data, 'siteWeb', 'NOT_FOUND')}")
        logger.info(f"   societeMere: {getattr(client_data, 'societeMere', 'NOT_FOUND')}")
        logger.info(f"   raisonSociale: {getattr(client_data, 'raisonSociale', 'NOT_FOUND')}")
        logger.info(f"   sigle: {getattr(client_data, 'sigle', 'NOT_FOUND')}")
        logger.info(f"   tribunalCommerce: {getattr(client_data, 'tribunalCommerce', 'NOT_FOUND')}")
        logger.info(f"   secteurActivite: {getattr(client_data, 'secteurActivite', 'NOT_FOUND')}")
        logger.info(f"   dateCreationSociete: {getattr(client_data, 'dateCreationSociete', 'NOT_FOUND')}")
        logger.info(f"   nomContactPrincipal: {getattr(client_data, 'nomContactPrincipal', 'NOT_FOUND')}")
        logger.info(f"   fonctionContactPrincipal: {getattr(client_data, 'fonctionContactPrincipal', 'NOT_FOUND')}")
    
    try:
        logger.info("📦 Creating DocumentService instance")
        service = DocumentService(session)
        logger.info("🔄 Calling service.create_client_with_documents()")
        result = await service.create_client_with_documents(client_data)
        logger.info(f"✅ create_client_with_documents successful, returning: {result}")
        return result
    except Exception as e:
        logger.error(f"❌ create_client_with_documents failed with error: {str(e)}")
        logger.error(f"❌ Error type: {type(e).__name__}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/clients/{client_id}/documents", response_model=List[DocumentResponse])
async def get_client_documents(
    client_id: int,
    session: AsyncSession = Depends(get_session)
):
    """Get all documents for a specific client"""
    logger.info(f"🔍 get_client_documents endpoint called for client_id: {client_id}")
    try:
        service = DocumentService(session)
        return await service.get_client_documents(client_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/clients/{client_id}/adherents", response_model=List[AdherentResponse])
async def get_client_adherents(
    client_id: int,
    session: AsyncSession = Depends(get_session)
):
    """Get all adherents for a specific client"""
    logger.info(f"🔍 get_client_adherents endpoint called for client_id: {client_id}")
    try:
        service = DocumentService(session)
        return await service.get_client_adherents(client_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    client_id: int = Form(None),
    session: AsyncSession = Depends(get_session)
):
    """Upload a document file"""
    logger.info(f"🔍 upload_document endpoint called for file: {file.filename}, client_id: {client_id}")
    try:
        # Create uploads directory if it doesn't exist
        # Go up one directory level from controller/ to app/ then into uploads/
        current_dir = os.path.dirname(os.path.abspath(__file__))
        upload_dir = os.path.join(os.path.dirname(current_dir), "uploads")
        
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
            logger.info(f"📁 Created uploads directory: {upload_dir}")
        else:
            logger.info(f"📁 Uploads directory already exists: {upload_dir}")
        
        # Generate unique filename to avoid conflicts
        import uuid
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(upload_dir, unique_filename)
        
        logger.info(f"📁 Saving file to: {file_path}")
        
        # Save the file to disk
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        logger.info(f"✅ File saved successfully to disk")
        
        # Create document service instance
        service = DocumentService(session)
        
        # Store the document in the database
        document_data = {
            'fichierNom': file.filename,  # Original filename for display
            'fichierChemin': unique_filename,  # Store just the filename, not the full path
            'typeEntite': 'CLIENT',  # Default to CLIENT type
            'idDocType': None,  # No document type for now
            'idEntite': client_id,
            'instantTele': datetime.now()
        }
        
        logger.info(f"📥 Document data to store: {document_data}")
        
        # Create the document record
        document = await service.create_document(document_data)
        
        logger.info(f"✅ Document {file.filename} uploaded successfully with ID: {document.id}, stored at: {file_path}")
        
        return {
            "id": document.id,
            "filename": file.filename,  # Original filename
            "size": file.size,
            "content_type": file.content_type,
            "client_id": client_id,
            "file_path": unique_filename,  # UUID filename for storage
            "original_filename": file.filename,  # Original filename for display
            "message": "Document uploaded successfully"
        }
    except Exception as e:
        logger.error(f"❌ upload_document failed with error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{document_id}")
async def delete_document(
    document_id: int,
    session: AsyncSession = Depends(get_session)
):
    """Delete a document"""
    logger.info(f"🔍 delete_document endpoint called for document_id: {document_id}")
    try:
        service = DocumentService(session)
        success = await service.delete_document(document_id)
        if success:
            return {"message": "Document deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Document not found")
    except Exception as e:
        logger.error(f"❌ delete_document failed with error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/csv/{client_id}/{filename}")
async def serve_csv_file(
    client_id: int,
    filename: str,
    session: AsyncSession = Depends(get_session)
):
    """Serve CSV files for clients"""
    logger.info(f"🔍 serve_csv_file endpoint called for client_id: {client_id}, filename: {filename}")
    try:
        # Get the document record to verify it exists and belongs to the client
        service = DocumentService(session)
        documents = await service.get_client_documents(client_id)
        
        # Find the CSV document
        csv_document = next((doc for doc in documents if doc.fichierNom == filename), None)
        
        if not csv_document:
            raise HTTPException(status_code=404, detail="CSV file not found for this client")
        
        # Construct the file path for CSV files
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Check if the CSV file is stored in the uploads directory (new format)
        if csv_document.fichierChemin and not csv_document.fichierChemin.startswith('csv_adherents/'):
            # New format: file is stored in uploads directory
            # Go up one directory level from controller/ to app/ then into uploads/
            upload_dir = os.path.join(os.path.dirname(current_dir), "uploads")
            
            # Create uploads directory if it doesn't exist
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir, exist_ok=True)
                logger.info(f"📁 Created uploads directory: {upload_dir}")
            
            file_path = os.path.join(upload_dir, csv_document.fichierChemin)
            logger.info(f"📁 Using uploads directory path: {file_path}")
        else:
            # Old format: file is stored in csv_adherents directory
            csv_dir = os.path.join(current_dir, "csv_adherents", str(client_id))
            file_path = os.path.join(csv_dir, filename)
            
            # Create CSV directory if it doesn't exist
            if not os.path.exists(csv_dir):
                os.makedirs(csv_dir, exist_ok=True)
                logger.info(f"📁 Created CSV directory: {csv_dir}")
            logger.info(f"📁 Using CSV directory path: {file_path}")
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="CSV file not found on disk")
        
        # Return the CSV file
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type='text/csv'
        )
        
    except Exception as e:
        logger.error(f"❌ serve_csv_file failed with error: {str(e)}")
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(status_code=500, detail=str(e))
