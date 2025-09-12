"""
Data Platform Integrations for Metapython
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Union, Iterator
from pathlib import Path
import logging
import time
import hashlib
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass

# Optional dependencies
try:
    import boto3
    from botocore.exceptions import ClientError, NoCredentialsError
    HAS_BOTO3 = True
except ImportError:
    HAS_BOTO3 = False

try:
    from google.cloud import storage as gcs
    from google.cloud import bigquery
    HAS_GCP = True
except ImportError:
    HAS_GCP = False

try:
    from azure.storage.blob import BlobServiceClient
    HAS_AZURE = True
except ImportError:
    HAS_AZURE = False

try:
    import snowflake.connector
    HAS_SNOWFLAKE = True
except ImportError:
    HAS_SNOWFLAKE = False

try:
    from pyspark.sql import SparkSession, DataFrame as SparkDataFrame
    HAS_SPARK = True
except ImportError:
    HAS_SPARK = False
    # Create dummy for type hints
    SparkDataFrame = Any

logger = logging.getLogger(__name__)

@dataclass
class ConnectionConfig:
    """Configuration for data platform connections"""
    provider: str
    credentials: Dict[str, Any]
    region: Optional[str] = None
    endpoint_url: Optional[str] = None
    timeout: int = 30
    retry_attempts: int = 3

@dataclass
class StreamingConfig:
    """Configuration for streamed reading"""
    chunk_size: int = 10000
    max_chunks: Optional[int] = None
    validate_schema: bool = True
    compute_checksum: bool = True

class BaseConnector(ABC):
    """Base class for data platform connectors"""
    
    def __init__(self, config: ConnectionConfig):
        self.config = config
        self.connection = None
        
    @abstractmethod
    def connect(self) -> bool:
        """Establish connection to the platform"""
        pass
        
    @abstractmethod
    def disconnect(self) -> bool:
        """Close connection to the platform"""
        pass
        
    @abstractmethod
    def list_objects(self, prefix: str = "") -> List[str]:
        """List available objects/files"""
        pass
        
    @abstractmethod
    def read_data(self, source: str, **kwargs) -> pd.DataFrame:
        """Read data from source"""
        pass
    
    def validate_connection(self) -> Dict[str, Any]:
        """Validate connection and permissions"""
        try:
            if self.connect():
                test_result = self.list_objects()
                return {
                    'connected': True,
                    'accessible_objects': len(test_result) if test_result else 0,
                    'error': None
                }
            else:
                return {
                    'connected': False,
                    'error': 'Failed to connect'
                }
        except Exception as e:
            return {
                'connected': False,
                'error': str(e)
            }

class S3Connector(BaseConnector):
    """Amazon S3 connector with signed URLs and role-based auth"""
    
    def __init__(self, config: ConnectionConfig):
        super().__init__(config)
        if not HAS_BOTO3:
            raise ImportError("boto3 required for S3 integration. Install with: pip install boto3")
    
    def connect(self) -> bool:
        """Connect to S3 using AWS credentials"""
        try:
            # Create S3 client
            self.connection = boto3.client(
                's3',
                aws_access_key_id=self.config.credentials.get('access_key_id'),
                aws_secret_access_key=self.config.credentials.get('secret_access_key'),
                aws_session_token=self.config.credentials.get('session_token'),
                region_name=self.config.region,
                endpoint_url=self.config.endpoint_url
            )
            
            # Test connection
            self.connection.list_buckets()
            logger.info("Successfully connected to S3")
            return True
            
        except (ClientError, NoCredentialsError) as e:
            logger.error(f"S3 connection failed: {e}")
            return False
    
    def disconnect(self) -> bool:
        """Disconnect from S3"""
        self.connection = None
        return True
    
    def list_objects(self, bucket: str, prefix: str = "") -> List[str]:
        """List objects in S3 bucket"""
        if not self.connection:
            raise RuntimeError("Not connected to S3")
        
        try:
            objects = []
            paginator = self.connection.get_paginator('list_objects_v2')
            
            for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
                if 'Contents' in page:
                    objects.extend([obj['Key'] for obj in page['Contents']])
            
            return objects
            
        except ClientError as e:
            logger.error(f"Failed to list S3 objects: {e}")
            return []
    
    def read_data(self, bucket: str, key: str, 
                 file_format: str = 'csv', **kwargs) -> pd.DataFrame:
        """Read data from S3 object"""
        if not self.connection:
            raise RuntimeError("Not connected to S3")
        
        try:
            # Get object
            response = self.connection.get_object(Bucket=bucket, Key=key)
            
            # Read based on format
            if file_format.lower() == 'csv':
                return pd.read_csv(response['Body'], **kwargs)
            elif file_format.lower() == 'parquet':
                return pd.read_parquet(response['Body'], **kwargs)
            elif file_format.lower() == 'json':
                return pd.read_json(response['Body'], **kwargs)
            else:
                raise ValueError(f"Unsupported file format: {file_format}")
                
        except ClientError as e:
            logger.error(f"Failed to read S3 object {bucket}/{key}: {e}")
            raise
    
    def create_signed_url(self, bucket: str, key: str, 
                         expiration: int = 3600) -> str:
        """Create signed URL for temporary access"""
        if not self.connection:
            raise RuntimeError("Not connected to S3")
        
        try:
            url = self.connection.generate_presigned_url(
                'get_object',
                Params={'Bucket': bucket, 'Key': key},
                ExpiresIn=expiration
            )
            return url
            
        except ClientError as e:
            logger.error(f"Failed to create signed URL: {e}")
            raise

class GCSConnector(BaseConnector):
    """Google Cloud Storage connector"""
    
    def __init__(self, config: ConnectionConfig):
        super().__init__(config)
        if not HAS_GCP:
            raise ImportError("google-cloud-storage required for GCS integration")
    
    def connect(self) -> bool:
        """Connect to GCS using service account or default credentials"""
        try:
            # Use service account key if provided
            if 'service_account_path' in self.config.credentials:
                self.connection = gcs.Client.from_service_account_json(
                    self.config.credentials['service_account_path']
                )
            else:
                # Use default credentials
                self.connection = gcs.Client()
            
            # Test connection
            list(self.connection.list_buckets(max_results=1))
            logger.info("Successfully connected to GCS")
            return True
            
        except Exception as e:
            logger.error(f"GCS connection failed: {e}")
            return False
    
    def disconnect(self) -> bool:
        """Disconnect from GCS"""
        self.connection = None
        return True
    
    def list_objects(self, bucket_name: str, prefix: str = "") -> List[str]:
        """List objects in GCS bucket"""
        if not self.connection:
            raise RuntimeError("Not connected to GCS")
        
        try:
            bucket = self.connection.bucket(bucket_name)
            blobs = bucket.list_blobs(prefix=prefix)
            return [blob.name for blob in blobs]
            
        except Exception as e:
            logger.error(f"Failed to list GCS objects: {e}")
            return []
    
    def read_data(self, bucket_name: str, blob_name: str,
                 file_format: str = 'csv', **kwargs) -> pd.DataFrame:
        """Read data from GCS blob"""
        if not self.connection:
            raise RuntimeError("Not connected to GCS")
        
        try:
            bucket = self.connection.bucket(bucket_name)
            blob = bucket.blob(blob_name)
            
            # Download to memory
            content = blob.download_as_bytes()
            
            # Read based on format
            if file_format.lower() == 'csv':
                return pd.read_csv(content, **kwargs)
            elif file_format.lower() == 'parquet':
                return pd.read_parquet(content, **kwargs)
            elif file_format.lower() == 'json':
                return pd.read_json(content, **kwargs)
            else:
                raise ValueError(f"Unsupported file format: {file_format}")
                
        except Exception as e:
            logger.error(f"Failed to read GCS blob {bucket_name}/{blob_name}: {e}")
            raise

class AzureBlobConnector(BaseConnector):
    """Azure Blob Storage connector"""
    
    def __init__(self, config: ConnectionConfig):
        super().__init__(config)
        if not HAS_AZURE:
            raise ImportError("azure-storage-blob required for Azure integration")
    
    def connect(self) -> bool:
        """Connect to Azure Blob Storage"""
        try:
            # Use connection string or account key
            if 'connection_string' in self.config.credentials:
                self.connection = BlobServiceClient.from_connection_string(
                    self.config.credentials['connection_string']
                )
            else:
                account_url = f"https://{self.config.credentials['account_name']}.blob.core.windows.net"
                self.connection = BlobServiceClient(
                    account_url=account_url,
                    credential=self.config.credentials['account_key']
                )
            
            # Test connection
            list(self.connection.list_containers(max_results=1))
            logger.info("Successfully connected to Azure Blob Storage")
            return True
            
        except Exception as e:
            logger.error(f"Azure connection failed: {e}")
            return False
    
    def disconnect(self) -> bool:
        """Disconnect from Azure Blob Storage"""
        self.connection = None
        return True
    
    def list_objects(self, container_name: str, prefix: str = "") -> List[str]:
        """List blobs in Azure container"""
        if not self.connection:
            raise RuntimeError("Not connected to Azure")
        
        try:
            container_client = self.connection.get_container_client(container_name)
            blobs = container_client.list_blobs(name_starts_with=prefix)
            return [blob.name for blob in blobs]
            
        except Exception as e:
            logger.error(f"Failed to list Azure blobs: {e}")
            return []
    
    def read_data(self, container_name: str, blob_name: str,
                 file_format: str = 'csv', **kwargs) -> pd.DataFrame:
        """Read data from Azure blob"""
        if not self.connection:
            raise RuntimeError("Not connected to Azure")
        
        try:
            blob_client = self.connection.get_blob_client(
                container=container_name, blob=blob_name
            )
            
            # Download blob content
            content = blob_client.download_blob().readall()
            
            # Read based on format
            if file_format.lower() == 'csv':
                return pd.read_csv(content, **kwargs)
            elif file_format.lower() == 'parquet':
                return pd.read_parquet(content, **kwargs)
            elif file_format.lower() == 'json':
                return pd.read_json(content, **kwargs)
            else:
                raise ValueError(f"Unsupported file format: {file_format}")
                
        except Exception as e:
            logger.error(f"Failed to read Azure blob {container_name}/{blob_name}: {e}")
            raise

class BigQueryConnector(BaseConnector):
    """Google BigQuery connector for read-only access"""
    
    def __init__(self, config: ConnectionConfig):
        super().__init__(config)
        if not HAS_GCP:
            raise ImportError("google-cloud-bigquery required for BigQuery integration")
    
    def connect(self) -> bool:
        """Connect to BigQuery"""
        try:
            if 'service_account_path' in self.config.credentials:
                self.connection = bigquery.Client.from_service_account_json(
                    self.config.credentials['service_account_path']
                )
            else:
                self.connection = bigquery.Client()
            
            # Test connection
            list(self.connection.list_datasets(max_results=1))
            logger.info("Successfully connected to BigQuery")
            return True
            
        except Exception as e:
            logger.error(f"BigQuery connection failed: {e}")
            return False
    
    def disconnect(self) -> bool:
        """Disconnect from BigQuery"""
        self.connection = None
        return True
    
    def list_objects(self, project_id: str, dataset_id: str = "") -> List[str]:
        """List tables in BigQuery project/dataset"""
        if not self.connection:
            raise RuntimeError("Not connected to BigQuery")
        
        try:
            if dataset_id:
                # List tables in specific dataset
                tables = self.connection.list_tables(f"{project_id}.{dataset_id}")
                return [f"{dataset_id}.{table.table_id}" for table in tables]
            else:
                # List all datasets
                datasets = self.connection.list_datasets(project_id)
                return [dataset.dataset_id for dataset in datasets]
                
        except Exception as e:
            logger.error(f"Failed to list BigQuery objects: {e}")
            return []
    
    def read_data(self, query: str = None, table_id: str = None, 
                 limit: Optional[int] = None, **kwargs) -> pd.DataFrame:
        """Read data from BigQuery using query or table"""
        if not self.connection:
            raise RuntimeError("Not connected to BigQuery")
        
        try:
            if query:
                # Execute custom query
                if limit:
                    query = f"SELECT * FROM ({query}) LIMIT {limit}"
                job = self.connection.query(query)
                return job.to_dataframe()
                
            elif table_id:
                # Read from table
                query = f"SELECT * FROM `{table_id}`"
                if limit:
                    query += f" LIMIT {limit}"
                job = self.connection.query(query)
                return job.to_dataframe()
                
            else:
                raise ValueError("Either query or table_id must be provided")
                
        except Exception as e:
            logger.error(f"Failed to read BigQuery data: {e}")
            raise

class SnowflakeConnector(BaseConnector):
    """Snowflake connector for read-only access"""
    
    def __init__(self, config: ConnectionConfig):
        super().__init__(config)
        if not HAS_SNOWFLAKE:
            raise ImportError("snowflake-connector-python required for Snowflake integration")
    
    def connect(self) -> bool:
        """Connect to Snowflake"""
        try:
            self.connection = snowflake.connector.connect(
                user=self.config.credentials['user'],
                password=self.config.credentials['password'],
                account=self.config.credentials['account'],
                warehouse=self.config.credentials.get('warehouse'),
                database=self.config.credentials.get('database'),
                schema=self.config.credentials.get('schema'),
                region=self.config.region
            )
            
            logger.info("Successfully connected to Snowflake")
            return True
            
        except Exception as e:
            logger.error(f"Snowflake connection failed: {e}")
            return False
    
    def disconnect(self) -> bool:
        """Disconnect from Snowflake"""
        if self.connection:
            self.connection.close()
            self.connection = None
        return True
    
    def list_objects(self, database: str = "", schema: str = "") -> List[str]:
        """List tables in Snowflake database/schema"""
        if not self.connection:
            raise RuntimeError("Not connected to Snowflake")
        
        try:
            cursor = self.connection.cursor()
            
            if database and schema:
                query = f"SHOW TABLES IN SCHEMA {database}.{schema}"
            elif database:
                query = f"SHOW TABLES IN DATABASE {database}"
            else:
                query = "SHOW TABLES"
            
            cursor.execute(query)
            tables = cursor.fetchall()
            cursor.close()
            
            return [table[1] for table in tables]  # Table name is in second column
            
        except Exception as e:
            logger.error(f"Failed to list Snowflake tables: {e}")
            return []
    
    def read_data(self, query: str, **kwargs) -> pd.DataFrame:
        """Read data from Snowflake using SQL query"""
        if not self.connection:
            raise RuntimeError("Not connected to Snowflake")
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            
            # Fetch results
            columns = [desc[0] for desc in cursor.description]
            data = cursor.fetchall()
            cursor.close()
            
            return pd.DataFrame(data, columns=columns)
            
        except Exception as e:
            logger.error(f"Failed to read Snowflake data: {e}")
            raise

class SparkConnector:
    """Apache Spark DataFrame bridge"""
    
    def __init__(self, app_name: str = "MetapythonSpark"):
        if not HAS_SPARK:
            raise ImportError("pyspark required for Spark integration")
        
        self.app_name = app_name
        self.spark = None
    
    def connect(self) -> bool:
        """Start Spark session"""
        try:
            self.spark = SparkSession.builder \
                .appName(self.app_name) \
                .getOrCreate()
            
            logger.info("Successfully started Spark session")
            return True
            
        except Exception as e:
            logger.error(f"Spark connection failed: {e}")
            return False
    
    def disconnect(self) -> bool:
        """Stop Spark session"""
        if self.spark:
            self.spark.stop()
            self.spark = None
        return True
    
    def pandas_to_spark(self, df: pd.DataFrame) -> SparkDataFrame:
        """Convert Pandas DataFrame to Spark DataFrame"""
        if not self.spark:
            raise RuntimeError("Spark session not started")
        
        return self.spark.createDataFrame(df)
    
    def spark_to_pandas(self, df: SparkDataFrame) -> pd.DataFrame:
        """Convert Spark DataFrame to Pandas DataFrame"""
        return df.toPandas()
    
    def read_data(self, file_path: str, file_format: str = 'csv', **kwargs) -> SparkDataFrame:
        """Read data into Spark DataFrame"""
        if not self.spark:
            raise RuntimeError("Spark session not started")
        
        reader = self.spark.read
        
        if file_format.lower() == 'csv':
            return reader.csv(file_path, header=True, inferSchema=True, **kwargs)
        elif file_format.lower() == 'parquet':
            return reader.parquet(file_path, **kwargs)
        elif file_format.lower() == 'json':
            return reader.json(file_path, **kwargs)
        else:
            raise ValueError(f"Unsupported file format: {file_format}")

class StreamingReader:
    """Streamed data reading with schema inference and checksum validation"""
    
    def __init__(self, connector: BaseConnector, config: StreamingConfig):
        self.connector = connector
        self.config = config
        self.schema = None
        self.checksum = None
    
    def stream_data(self, source: str, **kwargs) -> Iterator[pd.DataFrame]:
        """Stream data in chunks with validation"""
        
        chunk_count = 0
        total_checksum = hashlib.md5()
        
        try:
            # Read first chunk to infer schema
            first_chunk = self._read_chunk(source, 0, self.config.chunk_size, **kwargs)
            
            if first_chunk.empty:
                logger.warning("No data found in source")
                return
            
            # Store schema for validation
            if self.config.validate_schema:
                self.schema = self._infer_schema(first_chunk)
            
            # Yield first chunk
            yield first_chunk
            
            if self.config.compute_checksum:
                total_checksum.update(first_chunk.to_csv(index=False).encode())
            
            chunk_count += 1
            
            # Continue reading chunks
            while True:
                if self.config.max_chunks and chunk_count >= self.config.max_chunks:
                    break
                
                chunk = self._read_chunk(
                    source, 
                    chunk_count * self.config.chunk_size, 
                    self.config.chunk_size, 
                    **kwargs
                )
                
                if chunk.empty:
                    break
                
                # Validate schema if required
                if self.config.validate_schema:
                    self._validate_chunk_schema(chunk)
                
                # Update checksum
                if self.config.compute_checksum:
                    total_checksum.update(chunk.to_csv(index=False).encode())
                
                yield chunk
                chunk_count += 1
            
            # Store final checksum
            if self.config.compute_checksum:
                self.checksum = total_checksum.hexdigest()
            
            logger.info(f"Streamed {chunk_count} chunks from {source}")
            
        except Exception as e:
            logger.error(f"Streaming failed for {source}: {e}")
            raise
    
    def _read_chunk(self, source: str, offset: int, limit: int, **kwargs) -> pd.DataFrame:
        """Read a chunk of data (implementation depends on connector type)"""
        # This is a simplified implementation
        # Real implementation would depend on specific connector capabilities
        try:
            if hasattr(self.connector, 'read_data_chunk'):
                return self.connector.read_data_chunk(source, offset, limit, **kwargs)
            else:
                # Fallback: read all data and slice (not efficient for large datasets)
                full_data = self.connector.read_data(source, **kwargs)
                return full_data.iloc[offset:offset+limit]
        except Exception as e:
            logger.warning(f"Failed to read chunk {offset}-{offset+limit}: {e}")
            return pd.DataFrame()
    
    def _infer_schema(self, df: pd.DataFrame) -> Dict[str, str]:
        """Infer schema from DataFrame"""
        return {col: str(dtype) for col, dtype in df.dtypes.items()}
    
    def _validate_chunk_schema(self, chunk: pd.DataFrame) -> None:
        """Validate chunk schema against expected schema"""
        if not self.schema:
            return
        
        chunk_schema = self._infer_schema(chunk)
        
        # Check for missing columns
        missing_cols = set(self.schema.keys()) - set(chunk_schema.keys())
        if missing_cols:
            raise ValueError(f"Missing columns in chunk: {missing_cols}")
        
        # Check for type mismatches (simplified)
        type_mismatches = []
        for col in chunk_schema:
            if col in self.schema and chunk_schema[col] != self.schema[col]:
                type_mismatches.append(f"{col}: expected {self.schema[col]}, got {chunk_schema[col]}")
        
        if type_mismatches:
            logger.warning(f"Schema type mismatches: {type_mismatches}")

class IntegrationManager:
    """Central manager for all data platform integrations"""
    
    def __init__(self):
        self.connectors: Dict[str, BaseConnector] = {}
        self.spark_connector: Optional[SparkConnector] = None
    
    def register_connector(self, name: str, connector: BaseConnector) -> None:
        """Register a data platform connector"""
        self.connectors[name] = connector
        logger.info(f"Registered connector: {name}")
    
    def get_connector(self, name: str) -> Optional[BaseConnector]:
        """Get registered connector by name"""
        return self.connectors.get(name)
    
    def list_connectors(self) -> List[str]:
        """List all registered connectors"""
        return list(self.connectors.keys())
    
    def test_all_connections(self) -> Dict[str, Dict[str, Any]]:
        """Test all registered connections"""
        results = {}
        
        for name, connector in self.connectors.items():
            logger.info(f"Testing connection: {name}")
            results[name] = connector.validate_connection()
        
        return results
    
    def create_s3_connector(self, config: ConnectionConfig) -> S3Connector:
        """Create and register S3 connector"""
        connector = S3Connector(config)
        self.register_connector('s3', connector)
        return connector
    
    def create_gcs_connector(self, config: ConnectionConfig) -> GCSConnector:
        """Create and register GCS connector"""
        connector = GCSConnector(config)
        self.register_connector('gcs', connector)
        return connector
    
    def create_azure_connector(self, config: ConnectionConfig) -> AzureBlobConnector:
        """Create and register Azure connector"""
        connector = AzureBlobConnector(config)
        self.register_connector('azure', connector)
        return connector
    
    def create_bigquery_connector(self, config: ConnectionConfig) -> BigQueryConnector:
        """Create and register BigQuery connector"""
        connector = BigQueryConnector(config)
        self.register_connector('bigquery', connector)
        return connector
    
    def create_snowflake_connector(self, config: ConnectionConfig) -> SnowflakeConnector:
        """Create and register Snowflake connector"""
        connector = SnowflakeConnector(config)
        self.register_connector('snowflake', connector)
        return connector
    
    def start_spark(self, app_name: str = "MetapythonSpark") -> SparkConnector:
        """Start Spark session"""
        self.spark_connector = SparkConnector(app_name)
        self.spark_connector.connect()
        return self.spark_connector

# Export main classes
__all__ = [
    'ConnectionConfig',
    'StreamingConfig',
    'BaseConnector',
    'S3Connector',
    'GCSConnector', 
    'AzureBlobConnector',
    'BigQueryConnector',
    'SnowflakeConnector',
    'SparkConnector',
    'StreamingReader',
    'IntegrationManager'
]