"""
Advanced Query Executor Module (Streamlined)

Main orchestrator for executing MongoDB-style queries against the plant database.
Coordinates between query operations and response formatting.

Author: Plant Database API
Created: Advanced Filtering System Implementation
"""

from typing import Dict, List, Any
import logging

# Import the focused modules
from utils.advanced_query_operations import (
    load_database_data,
    filter_table_data,
    join_filtered_data,
    apply_sorting
)
from utils.advanced_query_formatter import format_query_response
from utils.advanced_query_parser import QueryParseError

logger = logging.getLogger(__name__)

class QueryExecutionError(Exception):
    """Custom exception for query execution errors"""
    pass

def execute_advanced_query(parsed_query: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute a parsed advanced query and return formatted results.
    
    Args:
        parsed_query: Parsed query from AdvancedQueryParser
        
    Returns:
        Dict: Query results in requested format
        
    Raises:
        QueryExecutionError: If query execution fails
    """
    try:
        logger.info(f"Executing advanced query with {len(parsed_query.get('filters', {}))} table filters")
        
        # Step 1: Load all data from database
        all_data = load_database_data()
        
        # Step 2: Apply filters to each table
        filtered_data = apply_all_filters(all_data, parsed_query['filters'], parsed_query['join_type'])
        
        # Step 3: Join filtered data
        joined_results = join_filtered_data(filtered_data)
        
        # Step 4: Apply sorting if specified
        if parsed_query.get('sort'):
            joined_results = apply_sorting(joined_results, parsed_query['sort'])
        
        # Step 5: Apply limit
        if parsed_query.get('limit'):
            joined_results = joined_results[:parsed_query['limit']]
        
        # Step 6: Format response
        formatted_response = format_query_response(
            joined_results,
            parsed_query['response_format'],
            parsed_query['include']
        )
        
        # Step 7: Add metadata
        formatted_response['query_metadata'] = {
            'total_matches': len(joined_results),
            'applied_limit': parsed_query.get('limit'),
            'response_format': parsed_query['response_format'],
            'tables_queried': list(parsed_query['filters'].keys()),
            'execution_success': True
        }
        
        logger.info(f"Query executed successfully, returned {len(joined_results)} results")
        return formatted_response
        
    except Exception as e:
        logger.error(f"Error executing query: {e}")
        raise QueryExecutionError(f"Query execution failed: {str(e)}")

def apply_all_filters(all_data: Dict[str, List[Dict]], filters: Dict[str, List[Dict]], join_type: str) -> Dict[str, List[Dict]]:
    """
    Apply filters to each table's data.
    
    Args:
        all_data: All loaded data
        filters: Parsed filter conditions
        join_type: 'AND' or 'OR' for combining conditions
        
    Returns:
        Dict: Filtered data for each table
    """
    filtered_data = {}
    
    for table_name, table_data in all_data.items():
        if table_name in filters:
            table_filters = filters[table_name]
            filtered_records = filter_table_data(table_data, table_filters, join_type)
            filtered_data[table_name] = filtered_records
            logger.info(f"Filtered {table_name}: {len(table_data)} → {len(filtered_records)} records")
        else:
            # No filters for this table, include all data
            filtered_data[table_name] = table_data
    
    return filtered_data
