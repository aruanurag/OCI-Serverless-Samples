# -----------------------------------------------------------------------------
# Copyright (c) 2025 Oracle and/or its affiliates.
#
# Licensed under the Universal Permissive License v 1.0 as shown at
# https://oss.oracle.com/licenses/upl

# DO NOT ALTER OR REMOVE COPYRIGHT NOTICES OR THIS HEADER.
# -----------------------------------------------------------------------------

import io
import json
import oci
import os
import random
import string
import configparser
import logging
import traceback
from datetime import datetime
from fdk import response

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConfigError(Exception):
    """Custom exception for configuration errors"""
    pass

class LogGenerationError(Exception):
    """Custom exception for log generation errors"""
    pass

class OCIError(Exception):
    """Custom exception for OCI-related errors"""
    pass

def load_json_config(config_path):
    """Load configuration from JSON file with enhanced error handling"""
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
            logger.info(f"Successfully loaded JSON config from {config_path}")
            return config
    except FileNotFoundError:
        logger.warning(f"Config file not found: {config_path}")
        return {}
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in config file {config_path}: {e}")
        raise ConfigError(f"Invalid JSON format in {config_path}: {e}")
    except PermissionError as e:
        logger.error(f"Permission denied reading config file {config_path}: {e}")
        raise ConfigError(f"Permission denied reading {config_path}: {e}")
    except Exception as e:
        logger.error(f"Unexpected error reading config file {config_path}: {e}")
        raise ConfigError(f"Error reading {config_path}: {e}")

def load_ini_config(config_path):
    """Load configuration from INI file with enhanced error handling"""
    try:
        config = configparser.ConfigParser()
        config.read(config_path)
        
        # Convert INI to dict format
        if 'DEFAULT' in config:
            result = dict(config['DEFAULT'])
            logger.info(f"Successfully loaded INI config from {config_path}")
            return result
        else:
            logger.warning(f"No DEFAULT section found in INI config {config_path}")
            return {}
    except FileNotFoundError:
        logger.warning(f"Config file not found: {config_path}")
        return {}
    except configparser.Error as e:
        logger.error(f"Invalid INI format in config file {config_path}: {e}")
        raise ConfigError(f"Invalid INI format in {config_path}: {e}")
    except PermissionError as e:
        logger.error(f"Permission denied reading config file {config_path}: {e}")
        raise ConfigError(f"Permission denied reading {config_path}: {e}")
    except Exception as e:
        logger.error(f"Unexpected error reading config file {config_path}: {e}")
        raise ConfigError(f"Error reading {config_path}: {e}")

def load_config_file(config_path):
    """Load configuration from file based on extension with enhanced error handling"""
    if not config_path:
        logger.warning("No config file path provided")
        return {}
    
    try:
        if config_path.endswith('.json'):
            return load_json_config(config_path)
        elif config_path.endswith('.ini'):
            return load_ini_config(config_path)
        else:
            # Try JSON first, then INI
            config = load_json_config(config_path)
            if not config:
                config = load_ini_config(config_path)
            return config
    except Exception as e:
        logger.error(f"Failed to load config file {config_path}: {e}")
        return {}

def validate_config(config):
    """Validate configuration parameters"""
    errors = []
    
    # Check required fields
    if 'log_id' not in config or not config['log_id']:
        errors.append("log_id is required and cannot be empty")
    
    # Validate numeric fields
    try:
        num_messages = int(config.get('num_messages', 10))
        if num_messages <= 0:
            errors.append("num_messages must be greater than 0")
        if num_messages > 100000:
            errors.append("num_messages exceed 100000. for more, relax the validation in the validate_config def")
    except (ValueError, TypeError):
        errors.append("num_messages must be a valid integer")
    
    try:
        message_size = int(config.get('message_size', 256))
        if message_size <= 0:
            errors.append("message_size must be greater than 0")
        if message_size > 100000:
            errors.append("message_size cannot exceed 100000")
    except (ValueError, TypeError):
        errors.append("message_size must be a valid integer")
    
    if errors:
        raise ConfigError(f"Configuration validation failed: {'; '.join(errors)}")

def get_config():
    """Get configuration with fallback hierarchy and validation"""
    try:
        config = {}
        
        # Try to load from config file first
        config_file = os.getenv("CONFIG_FILE", "config.json")
        if os.path.exists(config_file):
            config.update(load_config_file(config_file))
            logger.info(f"Loaded config from file: {config_file}")
        else:
            logger.info(f"Config file not found: {config_file}, using defaults")
        
        # Override with environment variables
        env_config = {
            'num_messages': os.getenv("NUM_MESSAGES"),
            'message_size': os.getenv("MESSAGE_SIZE"),
            'log_id': os.getenv("LOG_ID")
        }
        
        # Only update with non-None environment variables
        for key, value in env_config.items():
            if value is not None:
                config[key] = value
                logger.info(f"Overriding {key} with environment variable: {value}")
        
        # Set defaults for missing values
        config.setdefault('num_messages', 10)
        config.setdefault('message_size', 256)
        config.setdefault('log_id', "your-log-id")
        
        # Convert numeric values
        try:
            config['num_messages'] = int(config['num_messages'])
            config['message_size'] = int(config['message_size'])
        except (ValueError, TypeError) as e:
            raise ConfigError(f"Invalid numeric configuration: {e}")
        
        # Validate configuration
        validate_config(config)
        
        logger.info(f"Final configuration: {config}")
        return config
        
    except Exception as e:
        logger.error(f"Configuration error: {e}")
        raise

def generate_log_message(size):
    """Generate a simple log message of specified size with error handling"""
    try:
        if size <= 0:
            raise LogGenerationError("Message size must be greater than 0")
        if size > 100000:
            raise LogGenerationError("Message size cannot exceed 100000")
        
        message = ''.join(random.choices(string.ascii_letters + string.digits, k=size))
        return message
    except Exception as e:
        logger.error(f"Error generating log message: {e}")
        raise LogGenerationError(f"Failed to generate log message: {e}")

def create_oci_client():
    """Create OCI client with error handling"""
    try:
        signer = oci.auth.signers.get_resource_principals_signer()
        logging_client = oci.loggingingestion.LoggingClient({}, signer=signer)
        logger.info("Successfully created OCI logging client")
        return logging_client
    except Exception as e:
        logger.error(f"Failed to create OCI client: {e}")
        raise OCIError(f"Failed to initialize OCI client: {e}")

def send_logs_to_oci(logging_client, log_id, entries, iso_time):
    """Send logs to OCI with error handling"""
    try:
        request = oci.loggingingestion.models.PutLogsDetails(
            specversion="1.0",
            log_entry_batches=[
                oci.loggingingestion.models.LogEntryBatch(
                    entries=entries,
                    source="oci-function-log-generator",
                    type="custom",
                    defaultlogentrytime=iso_time
                )
            ]
        )

        response = logging_client.put_logs(log_id=log_id, put_logs_details=request)
        logger.info(f"Successfully sent {len(entries)} logs to OCI")
        return response
        
    except oci.exceptions.ServiceError as e:
        logger.error(f"OCI service error: {e}")
        raise OCIError(f"OCI service error: {e}")
    except oci.exceptions.ClientError as e:
        logger.error(f"OCI client error: {e}")
        raise OCIError(f"OCI client error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error sending logs to OCI: {e}")
        raise OCIError(f"Failed to send logs to OCI: {e}")

def handler(ctx, data: io.BytesIO = None):
    """Main handler function with comprehensive error handling"""
    start_time = datetime.utcnow()
    
    try:
        logger.info("Starting log generation process")
        
        # Get configuration
        config = get_config()
        
        # Create OCI client
        logging_client = create_oci_client()
        
        # Generate timestamp
        now = datetime.utcnow()
        iso_time = now.isoformat() + "Z"
        
        # Generate log entries
        entries = []
        logger.info(f"Generating {config['num_messages']} log messages of size {config['message_size']}")
        
        for i in range(config['num_messages']):
            try:
                log_message = generate_log_message(config['message_size'])
                entries.append({
                    "data": log_message,
                    "id": f"log-{random.randint(100000, 999999)}",
                    "time": iso_time,
                })
            except LogGenerationError as e:
                logger.error(f"Failed to generate log message {i+1}: {e}")
                # Continue with other messages instead of failing completely
                continue
        
        if not entries:
            raise LogGenerationError("No log entries were successfully generated")
        
        # Send logs to OCI
        send_logs_to_oci(logging_client, config['log_id'], entries, iso_time)
        
        # Calculate execution time
        execution_time = (datetime.utcnow() - start_time).total_seconds()
        
        logger.info(f"Log generation completed successfully in {execution_time:.2f} seconds")
        
        return response.Response(
            ctx, 
            status_code=200,
            response_data=json.dumps({
                "status": "OK", 
                "count": len(entries),
                "config": config,
                "execution_time_seconds": execution_time,
                "timestamp": iso_time
            })
        )
        
    except ConfigError as e:
        logger.error(f"Configuration error: {e}")
        return response.Response(
            ctx, 
            status_code=400,
            response_data=json.dumps({
                "error": "Configuration error",
                "message": str(e),
                "type": "ConfigError"
            })
        )
        
    except LogGenerationError as e:
        logger.error(f"Log generation error: {e}")
        return response.Response(
            ctx, 
            status_code=500,
            response_data=json.dumps({
                "error": "Log generation error",
                "message": str(e),
                "type": "LogGenerationError"
            })
        )
        
    except OCIError as e:
        logger.error(f"OCI error: {e}")
        return response.Response(
            ctx, 
            status_code=500,
            response_data=json.dumps({
                "error": "OCI service error",
                "message": str(e),
                "type": "OCIError"
            })
        )
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return response.Response(
            ctx, 
            status_code=500,
            response_data=json.dumps({
                "error": "Internal server error",
                "message": str(e),
                "type": "UnexpectedError"
            })
        )


