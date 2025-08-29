# Client Cleanup Mechanism

## Overview

The client cleanup mechanism automatically handles the cleanup of associated clients when a principal client is deleted. This ensures that when a principal client is removed from the system, all associated clients automatically return to the main clients table.

## How It Works

### 1. Automatic Cleanup on Client Deletion

When a client is deleted using the `DELETE /api/clients/{client_id}` endpoint, the system automatically:

1. **Identifies all relations** where the deleted client is either:
   - A principal client (`idClientPrincipal`)
   - An associated client (`idClientLie`)

2. **Deletes all related records** in the correct order:
   - Client relations (both as principal and associate)
   - Opportunities
   - Contracts
   - Adherents (flotte_auto, assure_sante, adherents_contrat)
   - Documents
   - Particulier/Societe records
   - Main client record

3. **Verifies cleanup** by checking that no relations remain for the deleted client

### 2. Impact on Associated Clients

When a principal client is deleted:
- **All `ClientRelation` records are removed** where the deleted client was the principal
- **Associated clients automatically become visible** in the main `ClientsPage` table
- **The `isAssociated` field becomes `false`** for those clients
- **No manual intervention is required**

## API Endpoints

### Delete Client (with automatic cleanup)
```
DELETE /api/clients/{client_id}
```
- Automatically cleans up all relations
- Returns associated clients to main table
- Logs detailed cleanup information

### Verify Cleanup
```
POST /api/clients/{client_id}/verify-cleanup
```
- Verifies that a deleted client has been properly cleaned up
- Returns cleanup status

### Force Cleanup of Orphaned Relations
```
POST /api/clients/cleanup-orphaned-relations
```
- Manually cleans up any orphaned relations
- Useful for maintenance and data integrity
- Returns count of cleaned relations

## Database Operations

### Client Relations Cleanup
```sql
-- Delete all relations where the client is involved (as principal or associate)
DELETE FROM clients_relations 
WHERE "idClientPrincipal" = :client_id OR "idClientLie" = :client_id
```

### Verification Query
```sql
-- Verify no relations remain for the deleted client
SELECT COUNT(*) FROM clients_relations 
WHERE "idClientPrincipal" = :client_id OR "idClientLie" = :client_id
```

### Orphaned Relations Detection
```sql
-- Find relations where either client no longer exists
SELECT cr.id FROM clients_relations cr
LEFT JOIN clients c1 ON cr."idClientPrincipal" = c1.id
LEFT JOIN clients c2 ON cr."idClientLie" = c2.id
WHERE c1.id IS NULL OR c2.id IS NULL
```

## Logging

The system provides comprehensive logging for all cleanup operations:

```
🗑️ Starting deletion of client 123...
📋 Found 2 relations to delete for client 123:
   - Client 123 is principal for associate 456
   - Client 123 is principal for associate 789
🗑️ Deleted 2 client relations for client 123
🔄 Associated clients will now return to the main clients table
🔍 Verifying cleanup of client relations for client 123...
✅ Verification successful: No remaining relations for client 123
✅ Successfully deleted client 123 and all related records
```

## Testing

Use the provided test script to verify the cleanup mechanism:

```bash
cd backend/scripts
python test_client_cleanup.py
```

This script will:
1. Check the current state of client relations
2. Identify any orphaned relations
3. Show currently associated clients
4. Provide test scenarios for cleanup verification

## Benefits

1. **Automatic Cleanup**: No manual intervention required
2. **Data Integrity**: Prevents orphaned relations
3. **User Experience**: Associated clients automatically return to main table
4. **Audit Trail**: Comprehensive logging of all cleanup operations
5. **Maintenance**: Built-in verification and manual cleanup tools

## Error Handling

The system includes robust error handling:
- **Transaction Rollback**: If any cleanup step fails, all changes are rolled back
- **Detailed Logging**: Comprehensive error information for debugging
- **Verification**: Automatic verification that cleanup was successful
- **Manual Recovery**: Tools to manually clean up orphaned relations if needed

## Security Considerations

- **Authentication Required**: All cleanup endpoints require proper authentication
- **Authorization**: Only authorized users can delete clients
- **Audit Logging**: All cleanup operations are logged for security purposes
- **Transaction Safety**: All operations are wrapped in database transactions

## Maintenance

### Regular Cleanup
The system automatically handles cleanup during normal operations.

### Manual Cleanup
Use the orphaned relations cleanup endpoint for maintenance:
```bash
curl -X POST /api/clients/cleanup-orphaned-relations
```

### Monitoring
Monitor the logs for:
- Successful cleanup operations
- Verification results
- Any orphaned relations that need attention

## Troubleshooting

### Common Issues

1. **Client still appears as associated after deletion**
   - Check if the deletion transaction was committed
   - Verify no relations remain in the database
   - Use the verification endpoint to check cleanup status

2. **Orphaned relations detected**
   - Use the manual cleanup endpoint
   - Check for any database constraint violations
   - Review the logs for cleanup failures

3. **Cleanup verification fails**
   - Check database transaction logs
   - Verify database permissions
   - Review the cleanup process step by step

### Debug Commands

```bash
# Check current relations
SELECT * FROM clients_relations;

# Check for orphaned relations
SELECT cr.* FROM clients_relations cr
LEFT JOIN clients c1 ON cr."idClientPrincipal" = c1.id
LEFT JOIN clients c2 ON cr."idClientLie" = c2.id
WHERE c1.id IS NULL OR c2.id IS NULL;

# Verify specific client cleanup
SELECT COUNT(*) FROM clients_relations WHERE "idClientPrincipal" = 123 OR "idClientLie" = 123;
```
