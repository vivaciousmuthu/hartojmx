import streamlit as st
import json
from datetime import datetime
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom.minidom import parseString
import os
from urllib.parse import urlparse, parse_qs
from xml.sax.saxutils import escape
import re


st.set_page_config(page_title="HAR to JMX Converter", page_icon="📄", layout="centered")


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
    """Check if URL belongs to a social media platform"""
    if not url:
        return False
    url_lower = url.lower()
    social_media_domains = [
        'twitter.com', 'x.com', 'facebook.com', 'fb.com',
        'instagram.com', 'pinterest.com', 'linkedin.com', 'tiktok.com',
        'youtube.com', 'youtu.be', 'reddit.com', 'snapchat.com',
        'telegram.me', 'telegram.org', 'whatsapp.com', 'viber.com',
        'discord.com', 'connect.facebook.net', 'api.twitter.com', 'graph.facebook.com', 'ads.twitter.com', 'business.facebook.com', 'google-analytics.com', 'googletagmanager.com', 'googlesyndication.com'
    ]
    return any(domain in url_lower for domain in social_media_domains)


# Helper function to detect GraphQL requests
def is_graphql_request(request, url):
    """Check if the request is a GraphQL request"""
    if not isinstance(request, dict):
        return False
    
    url_lower = url.lower() if url else ""
    
    # Check for GraphQL indicators in URL
    if 'graphql' in url_lower:
        return True
    
    # Check for GraphQL in headers
    headers = request.get('headers', [])
    for header in headers:
        if isinstance(header, dict):
            header_name = header.get('name', '').lower()
            if 'content-type' in header_name:
                header_value = header.get('value', '').lower()
                if 'application/json' in header_value or 'graphql' in header_value:
                    # Check if body contains GraphQL query
                    post_data = request.get('postData', {})
                    body_text = post_data.get('text', '')
                    if body_text and ('query' in body_text.lower() or 'mutation' in body_text.lower()):
                        return True
    
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
            
            # Create sampler name
            sampler_type = 'GraphQL' if is_graphql else method
            sampler_name = f'{script_prefix}_T{idx:02d}_{request_index:02d}_{sampler_type}_{base_name}'

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

            # Handle GraphQL requests
            if is_graphql:
                graphql_data = parse_graphql_body(request.get('postData', {}).get('text', ''))
                
                # Set path
                full_path = parsed_url.path
                if parsed_url.query:
                    full_path += '?' + parsed_url.query
                SubElement(http_sampler, 'stringProp', {'name': 'HTTPSampler.path'}).text = full_path
                
                # Add GraphQL specific properties
                SubElement(http_sampler, 'boolProp', {'name': 'HTTPSampler.postBodyRaw'}).text = 'true'
                
                # Add Arguments (GraphQL query and variables)
                args_prop = SubElement(http_sampler, 'elementProp', {
                    'name': 'HTTPsampler.Arguments',
                    'elementType': 'Arguments',
                    'guiclass': 'HTTPArgumentsPanel',
                    'testclass': 'Arguments',
                    'testname': 'User Defined Variables',
                    'enabled': 'true'
                })
                collection_prod = SubElement(args_prop, 'collectionProp', {'name': 'Arguments.arguments'})
                
                # Add GraphQL body as raw request
                param_element = SubElement(collection_prod, 'elementProp', {
                    'name': '',
                    'elementType': 'HTTPArgument'
                })
                SubElement(param_element, 'boolProp', {'name': 'HTTPArgument.always_encode'}).text = 'false'
                body_text = request.get('postData', {}).get('text', '')
                if body_text:
                    body_text = sanitize_text(str(body_text) if not isinstance(body_text, str) else body_text)
                SubElement(param_element, 'stringProp', {'name': 'Argument.value'}).text = body_text
                SubElement(param_element, 'stringProp', {'name': 'Argument.metadata'}).text = '='
                SubElement(param_element, 'boolProp', {'name': 'HTTPArgument.use_equals'}).text = 'true'

            # Handle GET and HEAD requests
            elif method in ['GET', 'HEAD', 'DELETE', 'OPTIONS', 'TRACE']:
                parsed_url = urlparse(url)
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
                parsed_url = urlparse(url)
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


#Streamlit App
def main():
    

    st.title("HAR to JMX Converter")
    st.write("Upload a **.har** file to generate a standardized **.jmx (JMeter)** file 🚀🎯😊. After conversion, you can proceed with further script enhancements. \n\n **Note:** Please upload only one file at a time. We do not store any uploaded files on our server. Simply upload and export instantly.")
    st.write("This tool is designed to save you time! I hope you find it helpful. Please feel free to message me, if you have any issue or suggestions.")

    # New supported HTTP methods information
    st.info("✨ **New Features**: This converter now supports all HTTP methods (GET, HEAD, PUT, DELETE, OPTIONS, PATCH, TRACE) and **GraphQL requests**!")

    uploaded_file = st.file_uploader("Choose a recorded HAR file", type="har")

    st.subheader("Transaction controller grouped by a time gap")
    time_gap = st.slider("Time Gap Threshold (seconds)", min_value=1, max_value=15, value=5)

    st.subheader("Script Configuration")
    thread_group_name = st.text_input("Thread Group Name", value="S01_ProjectName_Scenario_Name", help="Enter script name in format: S01_ProjectName_ScenarioName or S02_ProjectName_ScenarioName", placeholder="S01_ProjectName_Scenario_Name")

    st.subheader("Optional Configuration Toggles")
    include_headers = st.toggle("Header Configuraiton (Cache, Cookie, Request Defaults)", value=False)
    include_listeners = st.toggle("Listeners Configuration (View Results Tree, Summary Report, Aggregate Report)", value=False)
    include_sampler = st.toggle("Sampler Configuration (Debug Sampler)", value=False)
    exclude_social_media = st.toggle("Exclude Social Media URLs (Twitter, Facebook, Instagram, Pinterest, etc.)", value=False)


    if st.button("Convert to JMX"):
        # Validate thread group name first
        is_valid, validation_message = validate_thread_group_name(thread_group_name)
        
        if not is_valid:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.error(validation_message)
            with col2:
                if st.button("Reset", key="reset_button_validation"):
                    st.rerun()
        elif uploaded_file is None:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.error("Upload file and then try again. Refresh the screen!!")
            with col2:
                if st.button("Reset", key="reset_button_upload"):
                    st.rerun()
        else:
            try:
                with st.spinner("Converting..."):
                    har_content = json.load(uploaded_file)
                    jmx_content = har_to_jmx(har_content,
                                             time_gap_threshold=time_gap,
                                             include_headers=include_headers,
                                             include_listeners=include_listeners,
                                             include_sampler=include_sampler,
                                             script_name=thread_group_name,
                                             exclude_social_media=exclude_social_media)
                    original_name = os.path.splitext(uploaded_file.name)[0]
                    output_filename = f"{original_name}_Converted_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jmx"

                    st.download_button(
                        label="Download JMX File",
                        data=jmx_content,
                        file_name=output_filename,
                        mime="application/xml"
                    )

                    st.success(f"Conversion Completed! Click on the \"Download JMX File\" button above to download your file. **{output_filename}**")
            except json.JSONDecodeError as e:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.error(f"❌ Invalid HAR file format. Please ensure the file is a valid JSON file. Error: {str(e)}")
                with col2:
                    if st.button("Reset", key="reset_button_json"):
                        st.rerun()
            except ValueError as e:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.error(f"❌ {str(e)}\n\n**Tip:** The HAR file may have many incomplete or empty entries. Valid entries are being filtered automatically, but this file doesn't contain enough valid requests to convert.")
                with col2:
                    if st.button("Reset", key="reset_button_value"):
                        st.rerun()
            except Exception as e:
                col1, col2 = st.columns([3, 1])
                with col1:
                    error_msg = str(e)
                    # Provide more helpful error messages
                    if "not well-formed" in error_msg or "invalid token" in error_msg:
                        st.error(f"❌ XML Parsing Error: The HAR file contains invalid characters or malformed data.\n\n**Details:** {error_msg}\n\n**Solution:** The converter automatically filters invalid entries and sanitizes data. If this error persists, the HAR file may be corrupted. Try recording a fresh HAR file.")
                    else:
                        st.error(f"❌ Conversion Error: {error_msg}\n\n**Tip:** This might be due to unsupported data in the HAR file. The converter has skipped invalid entries and will use valid ones.")
                with col2:
                    if st.button("Reset", key="reset_button_conversion"):
                        st.rerun()

    st.markdown("\n\n")
    st.divider()
    st.title("Next Step")

    jmeter_url = "https://jmeter.apache.org/download_jmeter.cgi"
    jmeter_plugin = "https://jmeter-plugins.org"
    #jmeter_tips_tricks = ""

    with st.expander("JMeter Pre-requisties"):
        st.write("You must download the latest version of **JMeter version 5.6.3** and set it up in your local machine.")
        st.info(f"Click the links to download the [Jmeter (Binaries)]({jmeter_url}) and [JMeter Plugins]({jmeter_plugin})")
        st.markdown("**Note:** if you're using an older version of **JMeter (Less than 5.6.3)**, you may encounter compatibility issues with the generated JMX files. To avoid such issues, please set up to **JMeter 5.6.3** version on your machine.")


    with st.expander("JMeter Tips and Tricks"):
        st.subheader("Here are some useful tips and tricks to help you get started with JMeter:")
        st.write("- **Understand the Basics**: Familiarize yourself with JMeter's interface, components, and terminology. Knowing how to navigate the tool will make your experience smoother.")
        st.write("- **Use Thread Groups Wisely**: Thread Groups simulate user activity. Start with a small number of threads and gradually increase to avoid overwhelming your system.")
        st.write("- **Leverage Assertions**: Use assertions to validate responses and ensure your application behaves as expected under load.")
        st.write("- **Monitor Resource Usage**: Keep an eye on CPU, memory, and network usage during tests to identify potential bottlenecks.")
        st.write("- **Utilize Listeners**: Listeners provide valuable insights into test results. Use them to analyze performance metrics and identify issues.")
        st.write("- **Parameterize Tests**: Use CSV Data Set Config to parameterize your tests, allowing for more realistic and varied scenarios.")
        st.write("- **Run in Non-GUI Mode**: For large-scale load tests, execute JMeter from the command line in non-GUI mode using the -n and -t flags. This minimizes resource consumption and provides more accurate results.")
        st.info(f"- **Example Command**: \n jmeter -n -t my_test.jmx -l results.jtl -e -o ./mytest_report_folder \n\n Make sure 'mytest_report_folder' is empty or doesn't exist yet. \nThis command runs the test plan 'my_test.jmx' in non-GUI mode, logs results to 'results.jtl', and generates an HTML report in the specified folder.")
        
        st.subheader("New: HTTP Methods & GraphQL Support")
        st.write("- **All HTTP Methods Supported**: GET, HEAD, PUT, DELETE, OPTIONS, PATCH, TRACE")
        st.write("  - **GET/HEAD/DELETE/OPTIONS/TRACE**: Query parameters are automatically extracted from URLs")
        st.write("  - **POST/PUT/PATCH**: Supports both form-style parameters and raw JSON bodies")
        st.write("- **GraphQL Requests**: Automatically detected and converted with proper query, operation name, and variables extraction")
        st.write("  - **Detection**: URLs containing 'graphql' or requests with GraphQL headers are automatically identified")
        st.write("  - **Variables**: GraphQL variables are extracted and preserved in the JMX format")
        
        st.write("I will be updating more points soon...")


    



if __name__ == "__main__":
    main()
    
                    