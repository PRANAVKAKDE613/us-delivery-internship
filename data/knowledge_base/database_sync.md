# Database Sync & Data Pipeline Errors

## Known Issue Patterns
- **Sync Lag > 60 mins**: Secondary replica lagging behind primary write node during peak load.
- **Schema Drift Error**: Column type mismatch between source warehouse (BigQuery/Snowflake) and app store.

## Resolution Guidelines
1. Pause running pipelines before altering source schemas.
2. Re-trigger full sync for corrupted table slices from Admin Console > Pipelines.
3. Escalation: Contact Infrastructure / Data Platform team for replication queue resets.