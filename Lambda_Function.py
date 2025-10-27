import json
import os
import urllib.request

def lambda_handler(event, context):
    print("INSIDE LAMBDA FUNCTION")
    print(event)

    # Extract search term from event
    # Print the full event to see the structure
    print("Full event:", json.dumps(event, indent=2))
    
    # Extract parameters from Bedrock Agent event structure
    # Bedrock Agents pass parameters in event['parameters']
    search_term = None
    
    # Try to extract from parameters array (Bedrock Agent format)
    if 'parameters' in event:
        for param in event['parameters']:
            if param.get('name') == 'search_term':
                search_term = param.get('value')
                break
    
    # Fallback: try to extract from requestBody
    if not search_term and 'requestBody' in event:
        try:
            content = event['requestBody'].get('content', {})
            app_json = content.get('application/json', {})
            properties = app_json.get('properties', [])
            for prop in properties:
                if prop.get('name') == 'search_term':
                    search_term = prop.get('value')
                    break
        except Exception as e:
            print(f"Error extracting from requestBody: {e}") 
   
    if not search_term:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'search_term is required'})
        }
    
    # Read configuration from environment variables
    astra_token = os.environ.get('astra_token')
    astra_endpoint = os.environ.get('astra_endpoint')
    keyspace = os.environ.get('keyspace', 'default_keyspace')
    collection = os.environ.get('collection', 'quizprep_collection')
    
    # Construct API URL
    api_url = f"{astra_endpoint}/api/json/v1/{keyspace}/{collection}"
    
    # Vector similarity search query - searches based on semantic similarity
    query_data = {
        "find": {
            "sort": {
                "$vectorize": search_term  # This will find semantically similar content
            },
            "projection": {
                "$vectorize": 1  # Only return the text content
            },
            "options": {
                "limit": 5,  # Return top 5 most similar results
                "includeSimilarity": True  # Include similarity scores
            }
        }
    }
    
    try:
        # Prepare request
        headers = {
            'Content-Type': 'application/json',
            'X-Cassandra-Token': astra_token
        }
        
        # Make HTTP request
        req = urllib.request.Request(
            api_url,
            data=json.dumps(query_data).encode('utf-8'),
            headers=headers,
            method='POST'
        )
        
        # Execute request
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
        
        # Extract only the text content from $vectorize fields
        clean_results = []
        if 'data' in result and 'documents' in result['data']:
            for doc in result['data']['documents']:
                if '$vectorize' in doc:
                    clean_results.append(doc['$vectorize'])
        
        print("Full event:", json.dumps(clean_results, indent=2))
        
        return {
            "messageVersion": "1.0",
            "response": {
                "actionGroup": event['actionGroup'],
                "apiPath": event['apiPath'],
                "httpMethod": event['httpMethod'],
                "httpStatusCode": 200,
                "responseBody": {
                    "application/json": {
                        "body": json.dumps(clean_results)  # Proper JSON string
                    }
                }
            }
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
