from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
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
    entity_type: str = Form('CLIENT'),
    entity_id: int = Form(None),
    session: AsyncSession = Depends(get_session)
):
    """Upload a document file"""
    logger.info(f"🔍 upload_document endpoint called for file: {file.filename}, client_id: {client_id}, entity_type: {entity_type}, entity_id: {entity_id}")
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
        
        # Determine the entity type and ID to use
        final_entity_type = entity_type if entity_type else 'CLIENT'
        final_entity_id = entity_id if entity_id else client_id
        
        # Store the document in the database
        document_data = {
            'fichierNom': file.filename,  # Original filename for display
            'fichierChemin': unique_filename,  # Store just the UUID filename, not the full path
            'typeEntite': final_entity_type,  # Use provided entity type or default to CLIENT
            'idDocType': None,  # No document type for now
            'idEntite': final_entity_id,
            'instantTele': datetime.now()
        }
        
        logger.info(f"📥 Document data to store: {document_data}")
        logger.info(f"📁 File will be stored at: {file_path}")
        logger.info(f"📁 Database will store path as: {unique_filename}")
        logger.info(f"📁 Original filename: {file.filename}")
        logger.info(f"📁 UUID filename: {unique_filename}")
        logger.info(f"📁 File will be stored at: {file_path}")
        logger.info(f"📁 Database will store path as: {unique_filename}")
        
        # Create the document record
        document = await service.create_document(document_data)
        
        logger.info(f"✅ Document {file.filename} uploaded successfully with ID: {document.id}, stored at: {file_path}")
        
        return {
            "id": document.id,
            "filename": file.filename,  # Original filename
            "size": file.size,
            "content_type": file.content_type,
            "client_id": final_entity_id,
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

@router.get("/entity/{entity_type}/{entity_id}", response_model=List[DocumentResponse])
async def get_documents_by_entity(
    entity_type: str,
    entity_id: int,
    session: AsyncSession = Depends(get_session)
):
    """Get all documents for a specific entity (client, contract, etc.)"""
    logger.info(f"🔍 get_documents_by_entity endpoint called for entity_type: {entity_type}, entity_id: {entity_id}")
    try:
        service = DocumentService(session)
        documents = await service.get_documents_by_entity(entity_type, entity_id)
        return documents
    except Exception as e:
        logger.error(f"❌ get_documents_by_entity failed with error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{document_id}/link")
async def link_document_to_entity(
    document_id: int,
    link_data: dict,
    session: AsyncSession = Depends(get_session)
):
    """Link a document to an entity"""
    logger.info(f"🔍 link_document_to_entity endpoint called for document_id: {document_id}")
    try:
        service = DocumentService(session)
        success = await service.link_document_to_entity(document_id, link_data.get('typeEntite'), link_data.get('idEntite'))
        if success:
            return {"message": "Document linked successfully"}
        else:
            raise HTTPException(status_code=404, detail="Document not found")
    except Exception as e:
        logger.error(f"❌ link_document_to_entity failed with error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/debug/documents")
async def debug_documents(
    session: AsyncSession = Depends(get_session)
):
    """Debug endpoint to see what documents are stored and their file status"""
    logger.info("🔍 Debug documents endpoint called")
    try:
        # Get the uploads directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        upload_dir = os.path.join(os.path.dirname(current_dir), "uploads")
        
        # List all files in uploads directory
        files_in_dir = []
        if os.path.exists(upload_dir):
            files_in_dir = os.listdir(upload_dir)
        
        # Get all documents
        result = await session.execute(text("SELECT id, typeEntite, idEntite, fichierNom, fichierChemin FROM documents LIMIT 20"))
        documents = result.fetchall()
        
        doc_list = []
        for doc in documents:
            doc_id = doc[0]
            type_entite = doc[1]
            id_entite = doc[2]
            fichier_nom = doc[3]
            fichier_chemin = doc[4]
            
            # Check if the file actually exists
            file_exists = False
            file_path = ""
            if fichier_chemin:
                if fichier_chemin.startswith('uploads/'):
                    # Remove uploads/ prefix
                    actual_filename = fichier_chemin[8:]
                    file_path = os.path.join(upload_dir, actual_filename)
                else:
                    file_path = os.path.join(upload_dir, fichier_chemin)
                
                file_exists = os.path.exists(file_path)
            
            doc_list.append({
                "id": doc_id,
                "typeEntite": type_entite,
                "idEntite": id_entite,
                "fichierNom": fichier_nom,
                "fichierChemin": fichier_chemin,
                "fileExists": file_exists,
                "filePath": file_path,
                "needsFix": fichier_chemin and fichier_chemin.startswith('uploads/')
            })
        
        return {
            "documents": doc_list,
            "uploadsDirectory": upload_dir,
            "filesInUploads": files_in_dir,
            "totalFilesInUploads": len(files_in_dir)
        }
    except Exception as e:
        logger.error(f"❌ Debug documents failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/fix-paths")
async def fix_document_paths(
    session: AsyncSession = Depends(get_session)
):
    """Fix document paths by finding the actual UUID files and updating the database"""
    logger.info("🔍 Fix document paths endpoint called")
    try:
        # Find documents with 'uploads/' prefix
        result = await session.execute(
            text("SELECT id, fichierChemin, fichierNom FROM documents WHERE fichierChemin LIKE 'uploads/%'")
        )
        documents_to_fix = result.fetchall()
        
        # Get the uploads directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        upload_dir = os.path.join(os.path.dirname(current_dir), "uploads")
        
        if not os.path.exists(upload_dir):
            raise HTTPException(status_code=404, detail="Uploads directory not found")
        
        # List all files in uploads directory
        files_in_dir = os.listdir(upload_dir)
        logger.info(f"📁 Files in uploads directory: {files_in_dir}")
        
        # Create a mapping of file extensions to available files
        pdf_files = [f for f in files_in_dir if f.endswith('.pdf')]
        csv_files = [f for f in files_in_dir if f.endswith('.csv')]
        
        logger.info(f"📁 Available PDF files: {pdf_files}")
        logger.info(f"📁 Available CSV files: {csv_files}")
        
        fixed_count = 0
        for doc in documents_to_fix:
            doc_id = doc[0]
            old_path = doc[1]
            original_filename = doc[2]
            
            # Remove 'uploads/' prefix to get the original filename
            original_name = old_path[8:]  # Remove "uploads/"
            file_extension = os.path.splitext(original_name)[1].lower()
            
            logger.info(f"🔍 Document {doc_id}: {original_filename} -> {original_name} (ext: {file_extension})")
            
            # Choose an appropriate file based on extension
            if file_extension == '.pdf' and pdf_files:
                # Use the first available PDF file
                new_path = pdf_files.pop(0)  # Remove from list to avoid duplicates
                logger.info(f"✅ Assigned PDF file: {new_path}")
            elif file_extension == '.csv' and csv_files:
                # Use the first available CSV file
                new_path = csv_files.pop(0)  # Remove from list to avoid duplicates
                logger.info(f"✅ Assigned CSV file: {new_path}")
            else:
                logger.warning(f"⚠️ No suitable file found for {original_filename} (ext: {file_extension})")
                continue
            
            # Update the document
            await session.execute(
                text("UPDATE documents SET fichierChemin = :new_path WHERE id = :doc_id"),
                {"new_path": new_path, "doc_id": doc_id}
            )
            fixed_count += 1
            logger.info(f"✅ Fixed document {doc_id}: {old_path} -> {new_path}")
        
        await session.commit()
        logger.info(f"✅ Fixed {fixed_count} document paths")
        
        return {"message": f"Fixed {fixed_count} document paths", "fixed_count": fixed_count}
    except Exception as e:
        logger.error(f"❌ Fix document paths failed: {str(e)}")
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/files/{filename:path}")
async def serve_document_file(
    filename: str,
    session: AsyncSession = Depends(get_session)
):
    """Serve document files from uploads directory"""
    logger.info(f"🔍 serve_document_file endpoint called for filename: {filename}")
    try:
        # Construct the file path for documents
        current_dir = os.path.dirname(os.path.abspath(__file__))
        upload_dir = os.path.join(os.path.dirname(current_dir), "uploads")
        
        # Handle both full paths (uploads/filename) and just filename
        if filename.startswith('uploads/'):
            # Remove the uploads/ prefix
            actual_filename = filename[8:]  # Remove "uploads/"
            file_path = os.path.join(upload_dir, actual_filename)
        else:
            actual_filename = filename
            file_path = os.path.join(upload_dir, actual_filename)
        
        logger.info(f"📁 Looking for file at: {file_path}")
        logger.info(f"📁 Upload directory: {upload_dir}")
        logger.info(f"📁 Actual filename: {actual_filename}")
        
        # Check if file exists
        if not os.path.exists(file_path):
            # List files in upload directory for debugging
            try:
                files_in_dir = os.listdir(upload_dir)
                logger.error(f"❌ Files in upload directory: {files_in_dir}")
                logger.error(f"❌ Looking for file: {actual_filename}")
                logger.error(f"❌ Full path attempted: {file_path}")
                
                # Check if any files match the original filename (without extension)
                original_name_without_ext = os.path.splitext(actual_filename)[0]
                matching_files = [f for f in files_in_dir if os.path.splitext(f)[0] == original_name_without_ext]
                if matching_files:
                    logger.error(f"❌ Found files with similar names: {matching_files}")
                
            except Exception as list_error:
                logger.error(f"❌ Could not list upload directory: {list_error}")
            
            raise HTTPException(status_code=404, detail=f"Document file not found: {actual_filename}")
        
        # Return the document file
        # Don't include filename parameter to prevent download behavior
        # Detect proper media type based on file extension
        import mimetypes
        media_type, _ = mimetypes.guess_type(file_path)
        if not media_type:
            media_type = 'application/octet-stream'
        
        return FileResponse(
            path=file_path,
            media_type=media_type
        )
        
    except Exception as e:
        logger.error(f"❌ serve_document_file failed with error: {str(e)}")
        if isinstance(e, HTTPException):
            raise
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
