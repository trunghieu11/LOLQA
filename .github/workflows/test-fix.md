# Test Fix Notes

## Issues Fixed

1. **Missing Dependencies**: Added to `requirements-test.txt`:
   - `redis>=5.0.0`
   - `psycopg2-binary>=2.9.9`
   - `prometheus-client>=0.19.0`
   - `python-jose[cryptography]>=3.3.0`
   - `passlib[bcrypt]>=1.7.4`
   - `pydantic[email]>=2.9.0`

2. **Import Path Issues**: Fixed import paths in test files to handle:
   - Directory structure with hyphens (`auth-service` vs `auth_service`)
   - CI/CD environment path resolution
   - Added fallback import mechanisms

3. **Coverage Configuration**: Updated `pytest.ini` to include:
   - `shared` directory in coverage
   - `services` directory in coverage

## Test Files Updated

- `test_auth_service.py` - Fixed imports with fallback
- `test_llm_service.py` - Fixed imports with fallback
- `test_rag_service.py` - Fixed imports with fallback
- `test_data_pipeline_service.py` - Fixed imports with fallback
- `test_redis_client.py` - Added skip if redis not installed
- `test_db_client.py` - Added skip if psycopg2 not installed
- `test_metrics.py` - Added skip if prometheus_client not installed
- `test_microservices_integration.py` - Added skip if httpx not installed

