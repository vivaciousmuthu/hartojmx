import json
from datetime import datetime
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom.minidom import parseString
import os
from urllib.parse import urlparse, parse_qs
from xml.sax.saxutils import escape
import re


# Helper function to safely set text content in XML elements
def safe_set_text(element, text):
    """Safely set text content, escaping special XML characters"""
    if text is None:
        element.text = ''
    else:
        element.text = str(text) if not isinstance(text, str) else text


# Helper function to validate if an entry has required fields
def is_valid_entry(entry):
    """Check if an entry has the minimum required fields"""
    if not entry or not isinstance(entry, dict):
        return False
    
    request = entry.get('request')
    if not request or not isinstance(request, dict):
        return False
    
    # Check for required request fields
    required_fields = ['url', 'method']
    for field in required_fields:
        if field not in request or not request[field]:
            return False
    
    return True


# Helper function to sanitize text content for XML
def sanitize_text(text):
    """Remove or escape problematic characters for XML"""
    if not text:
        return ''
    if not isinstance(text, str):
        text = str(text)
    
    # Replace control characters that are invalid in XML
    # Remove control characters except tab, newline, carriage return
    text = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]', '', text)
    return text


# Helper function to extract script prefix from thread group name
def extract_script_prefix(thread_group_name):
    """Extract script prefix (e.g., S01) from thread group name"""
    if not thread_group_name:
        return 'S01'
    # Extract the prefix before the first underscore (e.g., 'S01' from 'S01_ProjectName_ScenarioName')
    parts = thread_group_name.split('_')
    if parts and parts[0].startswith('S') and len(parts[0]) >= 3:
        return parts[0]
    return 'S01'  # Default if format doesn't match


# Helper function to validate thread group name format
def validate_thread_group_name(thread_group_name):
    """
    Validate thread group name format: SXX_ProjectName_ScenarioName
    Returns tuple: (is_valid, error_message)
    """
    default_name = 'S01_ProjectName_Scenario_Name'
    
    # Check if using default name
    if thread_group_name == default_name:
        return False, "⚠️ Please change the Thread Group Name from the default. Use format: SXX_ProjectName_ScenarioName (e.g., S01_MyProject_LoginScenario)"
    
    # Check basic format
    if not thread_group_name or '_' not in thread_group_name:
        return False, "❌ Invalid format. Thread Group Name must contain underscores. Format: SXX_ProjectName_ScenarioName"
    
    parts = thread_group_name.split('_')
    
    # Should have at least 3 parts (SXX, ProjectName, ScenarioName)
    if len(parts) < 3:
        return False, "❌ Invalid format. Thread Group Name must have at least 3 parts separated by underscores. Format: SXX_ProjectName_ScenarioName"
    
    # First part should be SXX (S followed by 2 digits)
    script_prefix = parts[0]
    if not (script_prefix.startswith('S') and len(script_prefix) >= 3 and script_prefix[1:].isdigit()):
        return False, "❌ First part must start with 'S' followed by digits (e.g., S01, S02). Your format: " + script_prefix + "_..._..."
    
    # Check if other parts are empty
    for i, part in enumerate(parts[1:], 1):
        if not part or not part[0].isupper():
            return False, f"❌ Part {i+1} ('{part}') is invalid. Each part should start with an uppercase letter. Format: SXX_ProjectName_ScenarioName"
    
    return True, "Valid"


# Helper function to check if URL is a social media link
def is_social_media_url(url):
    """Check if URL belongs to a social media platform (domain-based, not substring matching)"""
    if not url:
        return False
    
    url_lower = url.lower()
    
    # Extract domain from URL
    try:
        # Get domain from URL (e.g., 'facebook.com' from 'https://www.facebook.com/page')
        from urllib.parse import urlparse
        parsed = urlparse(url_lower)
        domain = parsed.netloc  # e.g., 'www.facebook.com'
        
        if not domain:
            return False
        
        # Remove common subdomain prefixes (www, m, mobile)
        domain_clean = domain
        if domain_clean.startswith('www.'):
            domain_clean = domain_clean[4:]
        elif domain_clean.startswith('m.'):
            domain_clean = domain_clean[2:]
        elif domain_clean.startswith('mobile.'):
            domain_clean = domain_clean[7:]
        
        # Only include actual social media platforms
        social_media_domains = [
            'twitter.com', 'x.com', 'facebook.com', 'fb.com',
            'instagram.com', 'pinterest.com', 'linkedin.com', 'tiktok.com',
            'youtube.com', 'youtu.be', 'reddit.com', 'snapchat.com',
            'telegram.me', 'telegram.org', 'whatsapp.com', 'viber.com',
            'discord.com', 'connect.facebook.net', 'api.twitter.com', 'graph.facebook.com'
        ]
        
        # Check if domain matches any social media domain
        return any(domain_clean == soc_domain or domain_clean.endswith('.' + soc_domain) 
                   for soc_domain in social_media_domains)
    
    except Exception:
        return False


# Helper function to detect GraphQL requests
def is_graphql_request(request, url):
    """Check if the request is a GraphQL request based on URL and body structure"""
    if not isinstance(request, dict):
        return False
    
    url_lower = url.lower() if url else ""
    
    # Check for GraphQL indicators in URL (most reliable)
    if 'graphql' in url_lower:
        return True
    
    # For non-GraphQL URLs, check if the body has GraphQL operation syntax
    # This avoids false positives from REST APIs that have 'query' fields
    post_data = request.get('postData', {})
    body_text = post_data.get('text', '')
    
    if not body_text:
        return False
    
    try:
        # Try to parse as JSON
        body_json = json.loads(body_text) if isinstance(body_text, str) else body_text
        
        if not isinstance(body_json, dict):
            return False
        
        # GraphQL POST requests have this structure: {"query": "...", "operationName": "...", "variables": {...}}
        # Check if it has 'query' key with actual GraphQL operation syntax
        query_value = body_json.get('query', '')
        
        if not isinstance(query_value, str) or not query_value.strip():
            return False
        
        # Check for actual GraphQL operation syntax: starts with 'query', 'mutation', or 'subscription'
        # This distinguishes from regular REST APIs that might have a 'query' field
        query_lower = query_value.strip().lower()
        
        # Look for GraphQL operation keywords at start of query
        if (query_lower.startswith('query') or 
            query_lower.startswith('mutation') or 
            query_lower.startswith('subscription') or
            query_lower.startswith('{')):
            
            # Additionally, check if it looks like GraphQL by looking for field selections
            # GraphQL syntax includes { fieldName } pattern
            if '{' in query_value and '}' in query_value:
                return True
    
    except (json.JSONDecodeError, TypeError, AttributeError):
        pass
    
    return False


# Helper function to parse GraphQL request body
def parse_graphql_body(body_text):
    """Extract GraphQL query, mutation, operation name, and variables from request body"""
    graphql_data = {'operation': '', 'query': '', 'variables': ''}
    
    if not body_text:
        return graphql_data
    
    try:
        body_json = json.loads(body_text) if isinstance(body_text, str) else body_text
        if isinstance(body_json, dict):
            graphql_data['query'] = body_json.get('query', '')
            graphql_data['operation'] = body_json.get('operationName', '')
            variables = body_json.get('variables', {})
            graphql_data['variables'] = json.dumps(variables) if variables else ''
    except json.JSONDecodeError:
        pass
    
    return graphql_data


#add header configuration elements
def add_header_config(parent):
    #HTTP Cache Manager
    cache_manager = SubElement(parent, 'CacheManager', {
        'guiclass': 'CacheManagerGui',
        'testclass': 'CacheManager',
        'testname': 'HTTP Cache Manager',
        'enabled': 'true'
    })
    SubElement(cache_manager, 'boolProp', {'name': 'clearEachIteration'}).text = 'true'
    SubElement(parent, 'hashTree')

    #HTTP Cookie Manager
    cookie_manager = SubElement(parent, 'CookieManager', {
        'guiclass': 'CookiePanel',
        'testclass': 'CookieManager',
        'testname': 'HTTP Cookie Manager',
        'enabled': 'true'
    })
    SubElement(cookie_manager, 'boolProp', {'name': 'CookieManager.clearEachIteration'}).text = 'true'
    SubElement(parent, 'hashTree')

    #create the http Request Defaults Request
    request_defaults = SubElement(parent, 'ConfigTestElement', {
        'guiclass': 'HttpDefaultsGui',
        'testclass': 'ConfigTestElement',
        'testname': 'HTTP Request Defaults',
        'enabled': 'true'
    })

    #Add the HTTPSampler.Arguments elementProp
    element_prop = SubElement(request_defaults, 'elementProp', {
        'name': 'HTTPsampler.Arguments',
        'elementType': 'Arguments',
        'guiclass': 'HTTPArgumentsPanel',
        'testclass': 'Arguments',
        'testname': 'User Defined Variables',
        'enabled': 'true'
    })

    #Add the required collectionProp inside elementProp
    SubElement(element_prop, 'collectionProp', {'name': 'Arguments.arguments'})

    #Add other HTTP Request Defaults properties
    SubElement(request_defaults, 'stringProp', {'name': 'HTTPSampler.domain'}).text = ''
    SubElement(request_defaults, 'stringProp', {'name': 'HTTPSampler.port'}).text = ''
    SubElement(request_defaults, 'stringProp', {'name': 'HTTPSampler.protocol'}).text = ''
    SubElement(request_defaults, 'stringProp', {'name': 'HTTPSampler.contentEncoding'}).text = ''
    SubElement(request_defaults, 'stringProp', {'name': 'HTTPSampler.path'}).text = ''
    SubElement(request_defaults, 'stringProp', {'name': 'HTTPSampler.concurrentPool'}).text = ''
    SubElement(request_defaults, 'boolProp', {'name': 'HTTPSampler.concurrentDwn'}).text = 'true'
    

    #Add the hashTree node
    SubElement(parent, 'hashTree')


# Helper function to add query parameters to HTTP sampler
def add_query_parameters(http_sampler, url, query_params=None):
    """Add query parameters to HTTP sampler"""
    parsed_url = urlparse(url)
    
    # Merge query params from parsed URL and provided params
    query_params_combined = {}
    
    # From parsed URL
    for name, values in parse_qs(parsed_url.query, keep_blank_values=True).items():
        query_params_combined.setdefault(name, []).extend(values)
    
    # From provided params
    if query_params:
        for param in query_params:
            if isinstance(param, dict) and 'name' in param:
                query_params_combined[param['name']] = [param.get('value', '')]
    
    # Add query params to JMX if any exist
    if query_params_combined:
        args_prop = SubElement(http_sampler, 'elementProp', {
            'name': 'HTTPsampler.Arguments',
            'elementType': 'Arguments',
            'guiclass': 'HTTPArgumentsPanel',
            'testclass': 'Arguments',
            'testname': 'User Defined Variables',
            'enabled': 'true'
        })
        collection_prod = SubElement(args_prop, 'collectionProp', {'name': 'Arguments.arguments'})
        
        for name, values in query_params_combined.items():
            for value in values:
                param_element = SubElement(collection_prod, 'elementProp', {
                    'name': name,
                    'elementType': 'HTTPArgument'
                })
                SubElement(param_element, 'boolProp', {'name': 'HTTPArgument.always_encode'}).text = 'false'
                SubElement(param_element, 'stringProp', {'name': 'Argument.name'}).text = sanitize_text(name)
                SubElement(param_element, 'stringProp', {'name': 'Argument.value'}).text = sanitize_text(value)
                SubElement(param_element, 'stringProp', {'name': 'Argument.metadata'}).text = '='
                SubElement(param_element, 'boolProp', {'name': 'HTTPArgument.use_equals'}).text = 'true'


# Helper function to add body parameters to HTTP sampler (for POST, PUT, PATCH)
def add_body_parameters(http_sampler, post_data, is_raw=False):
    """Add body parameters to HTTP sampler"""
    args_prop = SubElement(http_sampler, 'elementProp', {
        'name': 'HTTPsampler.Arguments',
        'elementType': 'Arguments',
        'guiclass': 'HTTPArgumentsPanel',
        'testclass': 'Arguments',
        'testname': 'User Defined Variables',
        'enabled': 'true'
    })
    collection_prod = SubElement(args_prop, 'collectionProp', {'name': 'Arguments.arguments'})
    
    has_params = 'params' in post_data
    has_text = 'text' in post_data
    
    if has_params:
        SubElement(http_sampler, 'stringProp', {'name': 'HTTPSampler.postBodyRaw'}).text = 'false'
        for param in post_data.get('params', []):
            if not isinstance(param, dict) or 'name' not in param:
                continue
            param_element = SubElement(collection_prod, 'elementProp', {
                'name': sanitize_text(param['name']),
                'elementType': 'HTTPArgument'
            })
            SubElement(param_element, 'boolProp', {'name': 'HTTPArgument.always_encode'}).text = 'false'
            SubElement(param_element, 'stringProp', {'name': 'Argument.name'}).text = sanitize_text(param['name'])
            SubElement(param_element, 'stringProp', {'name': 'Argument.value'}).text = sanitize_text(param.get('value', ''))
            SubElement(param_element, 'stringProp', {'name': 'Argument.metadata'}).text = '='
            SubElement(param_element, 'boolProp', {'name': 'HTTPArgument.use_equals'}).text = 'true'
    
    elif has_text or is_raw:
        SubElement(http_sampler, 'boolProp', {'name': 'HTTPSampler.postBodyRaw'}).text = 'true'
        param_element = SubElement(collection_prod, 'elementProp', {
            'name': '',
            'elementType': 'HTTPArgument'
        })
        SubElement(param_element, 'boolProp', {'name': 'HTTPArgument.always_encode'}).text = 'false'
        body_text = post_data.get('text', '')
        if body_text:
            body_text = sanitize_text(str(body_text) if not isinstance(body_text, str) else body_text)
        SubElement(param_element, 'stringProp', {'name': 'Argument.value'}).text = body_text
        SubElement(param_element, 'stringProp', {'name': 'Argument.metadata'}).text = '='
        SubElement(param_element, 'boolProp', {'name': 'HTTPArgument.use_equals'}).text = 'true'


# Helper function to add headers to HTTP sampler
def add_headers_to_sampler(sampler_hash_tree, headers):
    """Add headers to HTTP sampler"""
    header_manager = SubElement(sampler_hash_tree, 'HeaderManager', {
        'guiclass': 'HeaderPanel',
        'testclass': 'HeaderManager',
        'testname': 'HTTP Header Manager',
        'enabled': 'true'
    })
    collection_prop = SubElement(header_manager, 'collectionProp', {'name': 'HeaderManager.headers'})
    for header in headers:
        # Validate header structure
        if not isinstance(header, dict) or 'name' not in header or 'value' not in header:
            continue
        
        # Skip HTTP/2 pseudo headers
        if header['name'].startswith(':'):
            continue
        
        header_element = SubElement(collection_prop, 'elementProp', {
            'name': sanitize_text(header['name']),
            'elementType': 'Header'
        })
        SubElement(header_element, 'stringProp', {'name': 'Header.name'}).text = sanitize_text(header['name'])
        SubElement(header_element, 'stringProp', {'name': 'Header.value'}).text = sanitize_text(header['value'])
    
    SubElement(sampler_hash_tree, 'hashTree')


# Helper function to create GraphQL HTTP Request sampler
def create_graphql_sampler(transaction_hash_tree, script_prefix, idx, request_index, base_name, domain, protocol, port, path, query_string, request, graphql_data):
    """
    Create a GraphQL HTTP Request using HTTPSamplerProxy with JSON body.
    GraphQL requests are standard POST requests with JSON-formatted body containing:
    - query: the GraphQL query/mutation
    - operationName (optional): the operation name for multi-operation documents
    - variables (optional): GraphQL variables as JSON object
    """
    sampler_name = f'{script_prefix}_T{idx:02d}_{request_index:02d}_GraphQL_{base_name}'
    
    # Use HTTPSamplerProxy for GraphQL (the standard JMeter HTTP sampler)
    http_sampler = SubElement(transaction_hash_tree, 'HTTPSamplerProxy', {
        'guiclass': 'HttpTestSampleGui',
        'testclass': 'HTTPSamplerProxy',
        'testname': sampler_name,
        'enabled': 'true'
    })
    
    # Set server properties
    SubElement(http_sampler, 'stringProp', {'name': 'HTTPSampler.domain'}).text = domain
    SubElement(http_sampler, 'stringProp', {'name': 'HTTPSampler.protocol'}).text = protocol
    SubElement(http_sampler, 'stringProp', {'name': 'HTTPSampler.port'}).text = port
    
    # Set path with query string
    full_path = path
    if query_string:
        full_path += '?' + query_string
    SubElement(http_sampler, 'stringProp', {'name': 'HTTPSampler.path'}).text = full_path
    
    # GraphQL is always POST
    SubElement(http_sampler, 'stringProp', {'name': 'HTTPSampler.method'}).text = 'POST'
    
    # Standard HTTP properties
    SubElement(http_sampler, 'stringProp', {'name': 'HTTPSampler.contentEncoding'}).text = 'UTF-8'
    SubElement(http_sampler, 'boolProp', {'name': 'HTTPSampler.follow_redirects'}).text = 'false'
    SubElement(http_sampler, 'boolProp', {'name': 'HTTPSampler.auto_redirects'}).text = 'false'
    SubElement(http_sampler, 'boolProp', {'name': 'HTTPSampler.use_keepalive'}).text = 'true'
    SubElement(http_sampler, 'boolProp', {'name': 'HTTPSampler.DO_MULTIPART_POST'}).text = 'false'
    SubElement(http_sampler, 'stringProp', {'name': 'HTTPSampler.embedded_url_re'}).text = ''
    
    # Build GraphQL JSON body
    graphql_body = {}
    
    # Add query (required)
    query_text = graphql_data.get('query', '')
    if query_text:
        graphql_body['query'] = query_text
    
    # Add operationName if present
    operation_name = graphql_data.get('operation', '')
    if operation_name:
        graphql_body['operationName'] = operation_name
    
    # Add variables if present (as object, not string)
    variables_text = graphql_data.get('variables', '')
    if variables_text:
        try:
            graphql_body['variables'] = json.loads(variables_text) if isinstance(variables_text, str) else variables_text
        except json.JSONDecodeError:
            # If variables is not valid JSON, skip it
            pass
    
    # Convert body to JSON string
    graphql_json_body = json.dumps(graphql_body)
    
    # Add body as HTTP Arguments (raw POST body)
    args_prop = SubElement(http_sampler, 'elementProp', {
        'name': 'HTTPsampler.Arguments',
        'elementType': 'Arguments',
        'guiclass': 'HTTPArgumentsPanel',
        'testclass': 'Arguments',
        'testname': 'User Defined Variables',
        'enabled': 'true'
    })
    collection_prod = SubElement(args_prop, 'collectionProp', {'name': 'Arguments.arguments'})
    
    # Set as raw body (not form parameters)
    SubElement(http_sampler, 'boolProp', {'name': 'HTTPSampler.postBodyRaw'}).text = 'true'
    
    param_element = SubElement(collection_prod, 'elementProp', {
        'name': '',
        'elementType': 'HTTPArgument'
    })
    SubElement(param_element, 'boolProp', {'name': 'HTTPArgument.always_encode'}).text = 'false'
    SubElement(param_element, 'stringProp', {'name': 'Argument.value'}).text = sanitize_text(graphql_json_body)
    SubElement(param_element, 'stringProp', {'name': 'Argument.metadata'}).text = '='
    SubElement(param_element, 'boolProp', {'name': 'HTTPArgument.use_equals'}).text = 'true'
    
    # Create hashTree for the sampler
    sampler_hash_tree = SubElement(transaction_hash_tree, 'hashTree')
    
    # Add headers to the sampler's hashTree using add_headers_to_sampler
    # Make sure Content-Type is set to application/json for GraphQL
    headers = request.get('headers', [])
    
    # Add Content-Type header if not present
    content_type_found = False
    for header in headers:
        if isinstance(header, dict) and header.get('name', '').lower() == 'content-type':
            content_type_found = True
            break
    
    if not content_type_found:
        headers = list(headers) + [{'name': 'Content-Type', 'value': 'application/json'}]
    
    add_headers_to_sampler(sampler_hash_tree, headers)
    
    return http_sampler



# Add listener configuration elements
def add_listener_config(parent):
    #View Results Tree Listener
    view_results = SubElement(parent, 'ResultCollector', {
        'guiclass': 'ViewResultsFullVisualizer',
        'testclass': 'ResultCollector',
        'testname': 'View Results Tree',
        'enabled': 'true'
    })
    SubElement(view_results, 'boolProp', {'name': 'filename'}).text = ''
    SubElement(view_results, 'objProp', {'name': 'saveConfig'})
    SubElement(parent, 'hashTree')

    #Summary Report Listener
    summary_report = SubElement(parent, 'ResultCollector', {
        'guiclass': 'StatVisualizer',
        'testclass': 'ResultCollector',
        'testname': 'Summary Report',
        'enabled': 'true'
    })
    SubElement(summary_report, 'boolProp', {'name': 'filename'}).text = 'false'
    SubElement(summary_report, 'objProp', {'name': 'saveConfig'})
    SubElement(parent, 'hashTree')

    #aggregate Report Listener
    aggregate_report = SubElement(parent, 'ResultCollector', {
        'guiclass': 'StatVisualizer',
        'testclass': 'ResultCollector',
        'testname': 'Aggregate Report',
        'enabled': 'true'
    })
    SubElement(aggregate_report, 'stringProp', {'name': 'filename'}).text = ''
    SubElement(aggregate_report, 'objProp', {'name': 'saveConfig'})
    SubElement(parent, 'hashTree')


# Add Debug Sampler
def add_debug_sampler(parent):
    debug_sampler = SubElement(parent, 'DebugSampler', {
        'guiclass': 'TestBeanGUI',
        'testclass': 'DebugSampler',
        'testname': 'Debug Sampler',
        'enabled': 'true'
    })
    SubElement(debug_sampler, 'boolProp', {'name': 'displayJMeterProperties'}).text = 'false'
    SubElement(debug_sampler, 'boolProp', {'name': 'displaySystemProperties'}).text = 'false'
    SubElement(debug_sampler, 'boolProp', {'name': 'displaySamplerProperties'}).text = 'true'
    SubElement(debug_sampler, 'boolProp', {'name': 'displayThreadName'}).text = 'true'
    SubElement(debug_sampler, 'boolProp', {'name': 'displayVariables'}).text = 'true'
    SubElement(parent, 'hashTree')   



#Converting HAR to JMX using time gap strategy
def har_to_jmx(har_data, time_gap_threshold=5, include_headers=False, include_listeners=False, include_sampler=False, script_name='S01_ProjectName_Scenario_Name', exclude_social_media=False):
    jmeter_test_plan = Element('jmeterTestPlan', {
        'version': '1.2',
        'properties': '5.0',
        'jmeter': '5.6.3'
    })
    root_hash_tree = SubElement(jmeter_test_plan, 'hashTree')

    if include_headers:
        add_header_config(root_hash_tree)

    # Extract script prefix from script name
    script_prefix = extract_script_prefix(script_name)
    
    #Thread Group
    thread_group = SubElement(root_hash_tree, 'ThreadGroup', {
        'guiclass': 'ThreadGroupGui',
        'testclass': 'ThreadGroup',
        'testname': script_name,
        'enabled': 'true'
    })
    SubElement(thread_group, 'stringProp', {'name': 'ThreadGroup.on_sample_error'}).text = 'continue'
    loop_controller = SubElement(thread_group, 'elementProp', {
        'name': 'ThreadGroup.main_controller',
        'elementType': 'LoopController',
        'guiclass': 'LoopControlPanel',
        'testclass': 'LoopController',
        'testname': 'Loop Controller',
        'enabled': 'true'
    })
    SubElement(loop_controller, 'boolProp', {'name': 'LoopController.continue_forever'}).text = 'false'
    SubElement(loop_controller, 'stringProp', {'name': 'LoopController.loops'}).text = '1'
    SubElement(thread_group, 'stringProp', {'name': 'ThreadGroup.num_threads'}).text = '1'
    SubElement(thread_group, 'stringProp', {'name': 'ThreadGroup.ramp_time'}).text = '1'
    SubElement(thread_group, 'boolProp', {'name': 'ThreadGroup.scheduler'}).text = 'false'
    SubElement(thread_group, 'stringProp', {'name': 'ThreadGroup.duration'}).text = ''
    SubElement(thread_group, 'stringProp', {'name': 'ThreadGroup.delay'}).text = ''
    thread_hash_tree = SubElement(root_hash_tree, 'hashTree')

    entries = har_data['log']['entries']
    
    # Filter out invalid entries (e.g., empty objects, incomplete requests)
    valid_entries = [entry for entry in entries if is_valid_entry(entry)]
    
    # Filter out social media URLs if requested
    if exclude_social_media:
        valid_entries = [entry for entry in valid_entries if not is_social_media_url(entry['request'].get('url', ''))]
    
    if not valid_entries:
        raise ValueError("No valid HTTP requests found in the HAR file. All entries appear to be incomplete or malformed.")
    
    grouped_requests = {}
    transaction_index = 1
    last_time = None
    group_name = f'Transaction_{transaction_index}'
    grouped_requests[group_name] = []

    for entry in valid_entries:
        startedDateTime = entry.get('startedDateTime')
        if startedDateTime:
            try:
                current_time = datetime.strptime(startedDateTime, '%Y-%m-%dT%H:%M:%S.%fZ')
            except ValueError:
                try:
                    current_time = datetime.strptime(startedDateTime, '%Y-%m-%dT%H:%M:%SZ')
                except ValueError:
                    # If date parsing fails, skip this entry
                    continue
            if last_time and (current_time - last_time).total_seconds() > time_gap_threshold:
                transaction_index += 1
                group_name = f'Transaction_{transaction_index}'
                grouped_requests[group_name] = []
            last_time = current_time
        grouped_requests[group_name].append(entry)

    for idx, (group_name, grouped_requests) in enumerate(grouped_requests.items(), start=1):
        transaction_controller = SubElement(thread_hash_tree, 'TransactionController', {
            'guiclass': 'TransactionControllerGui',
            'testclass': 'TransactionController',
            'testname': f'{script_prefix}_T{str(idx).zfill(2)}_{group_name}',
            'enabled': 'true'
        })
        SubElement(transaction_controller, 'boolProp', {'name': 'TransactionController.includeTimers'}).text = 'false'
        transaction_hash_tree = SubElement(thread_hash_tree, 'hashTree')


        #for entry in group_entries:
        for request_index, entry in enumerate(grouped_requests, start=1):
            request = entry['request']
            url = request['url']
            method = request['method'].upper()
            protocol = url.split(':')[0] if ':' in url else 'http'
            domain = url.split('/')[2] if len(url.split('/')) > 2 else ''
            path = '/' + '/'.join(url.split('/')[3:]) if len(url.split('/')) > 3 else '/'

            port = ''
            if ':' in domain:
                domain, port = domain.split(':')
            else:
                port = '443' if protocol == 'https' else '80'

            parsed_url = urlparse(url)
            base_name = parsed_url.path.split('/')[-1] or 'root'
            
            # Check if this is a GraphQL request
            is_graphql = is_graphql_request(request, url)
            
            # Handle GraphQL requests with dedicated GraphQL sampler
            if is_graphql:
                graphql_data = parse_graphql_body(request.get('postData', {}).get('text', ''))
                create_graphql_sampler(transaction_hash_tree, script_prefix, idx, request_index, base_name, 
                                      domain, protocol, port, parsed_url.path, parsed_url.query, request, graphql_data)
            
            # Handle non-GraphQL HTTP requests
            else:
                # Create sampler name
                sampler_name = f'{script_prefix}_T{idx:02d}_{request_index:02d}_{method}_{base_name}'

                # Create HTTP sampler
                http_sampler = SubElement(transaction_hash_tree, 'HTTPSamplerProxy', {
                    'guiclass': 'HttpTestSampleGui',
                    'testclass': 'HTTPSamplerProxy',
                    'testname': sampler_name,
                    'enabled': 'true'
                })
                
                SubElement(http_sampler, 'stringProp', {'name': 'HTTPSampler.domain'}).text = domain
                SubElement(http_sampler, 'stringProp', {'name': 'HTTPSampler.protocol'}).text = protocol
                SubElement(http_sampler, 'stringProp', {'name': 'HTTPSampler.port'}).text = port
                SubElement(http_sampler, 'stringProp', {'name': 'HTTPSampler.method'}).text = method

                # Add standard HTTP properties
                SubElement(http_sampler, 'stringProp', {'name': 'HTTPSampler.contentEncoding'}).text = 'UTF-8'
                SubElement(http_sampler, 'boolProp', {'name': 'HTTPSampler.follow_redirects'}).text = 'false'
                SubElement(http_sampler, 'boolProp', {'name': 'HTTPSampler.auto_redirects'}).text = 'false'
                SubElement(http_sampler, 'boolProp', {'name': 'HTTPSampler.use_keepalive'}).text = 'true'
                SubElement(http_sampler, 'boolProp', {'name': 'HTTPSampler.DO_MULTIPART_POST'}).text = 'false'
                SubElement(http_sampler, 'stringProp', {'name': 'HTTPSampler.embedded_url_re'}).text = ''

                # Handle GET and HEAD requests
                if method in ['GET', 'HEAD', 'DELETE', 'OPTIONS', 'TRACE']:
                    SubElement(http_sampler, 'stringProp', {'name': 'HTTPSampler.path'}).text = parsed_url.path
                    
                    # Add query parameters for all GET/HEAD/DELETE/OPTIONS/TRACE requests
                    query_params_combined = {}
                    
                    # From parsed URL
                    for name, values in parse_qs(parsed_url.query, keep_blank_values=True).items():
                        query_params_combined.setdefault(name, []).extend(values)
                    
                    # From HAR queryString
                    if request.get('queryString'):
                        for param in request['queryString']:
                            query_params_combined[param['name']] = [param['value']]
                    
                    # Add query params to JMX if any exist
                    if query_params_combined:
                        args_prop = SubElement(http_sampler, 'elementProp', {
                            'name': 'HTTPsampler.Arguments',
                            'elementType': 'Arguments',
                            'guiclass': 'HTTPArgumentsPanel',
                            'testclass': 'Arguments',
                            'testname': 'User Defined Variables',
                            'enabled': 'true'
                        })
                        collection_prod = SubElement(args_prop, 'collectionProp', {'name': 'Arguments.arguments'})
                        
                        for name, values in query_params_combined.items():
                            for value in values:
                                param_element = SubElement(collection_prod, 'elementProp', {
                                    'name': name,
                                    'elementType': 'HTTPArgument'
                                })
                                SubElement(param_element, 'boolProp', {'name': 'HTTPArgument.always_encode'}).text = 'false'
                                SubElement(param_element, 'stringProp', {'name': 'Argument.name'}).text = sanitize_text(name)
                                SubElement(param_element, 'stringProp', {'name': 'Argument.value'}).text = sanitize_text(value)
                                SubElement(param_element, 'stringProp', {'name': 'Argument.metadata'}).text = '='
                                SubElement(param_element, 'boolProp', {'name': 'HTTPArgument.use_equals'}).text = 'true'

                # Handle POST, PUT, PATCH requests
                elif method in ['POST', 'PUT', 'PATCH']:
                    post_data = request.get('postData', {})
                    
                    has_params = 'params' in post_data
                    has_text = 'text' in post_data
                    
                    if has_params:
                        # Form-style body with parameters
                        SubElement(http_sampler, 'stringProp', {'name': 'HTTPSampler.path'}).text = parsed_url.path
                        add_body_parameters(http_sampler, post_data, is_raw=False)
                    
                    elif has_text:
                        # Raw body (JSON or other formats)
                        full_path = parsed_url.path
                        if parsed_url.query:
                            full_path += '?' + parsed_url.query
                        SubElement(http_sampler, 'stringProp', {'name': 'HTTPSampler.path'}).text = full_path
                        add_body_parameters(http_sampler, post_data, is_raw=True)
                    
                    else:
                        # No body
                        full_path = parsed_url.path
                        if parsed_url.query:
                            full_path += '?' + parsed_url.query
                        SubElement(http_sampler, 'stringProp', {'name': 'HTTPSampler.path'}).text = full_path

                # Add hashTree for HTTP Sampler
                sampler_hash_tree = SubElement(transaction_hash_tree, 'hashTree')
                
                # Add headers to sampler
                add_headers_to_sampler(sampler_hash_tree, request.get('headers', []))
    
    if include_listeners:
        add_listener_config(thread_hash_tree)

    if include_sampler:
        add_debug_sampler(thread_hash_tree)

    xml_str = tostring(jmeter_test_plan, encoding='unicode')
    pretty_xml = parseString(xml_str).toprettyxml(indent="  ")
    return pretty_xml


