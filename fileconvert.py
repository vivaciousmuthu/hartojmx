import streamlit as st
import json
from datetime import datetime
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom.minidom import parseString
import os
from urllib.parse import urlparse, parse_qs


st.set_page_config(page_title="HAR to JMX Converter", page_icon="📄", layout="centered")

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
def har_to_jmx(har_data, time_gap_threshold=5, include_headers=False, include_listeners=False, include_sampler=False):
    jmeter_test_plan = Element('jmeterTestPlan', {
        'version': '1.2',
        'properties': '5.0',
        'jmeter': '5.6.3'
    })
    root_hash_tree = SubElement(jmeter_test_plan, 'hashTree')

    if include_headers:
        add_header_config(root_hash_tree)

    
    #Thread Group
    thread_group = SubElement(root_hash_tree, 'ThreadGroup', {
        'guiclass': 'ThreadGroupGui',
        'testclass': 'ThreadGroup',
        'testname': 'S01_ProjectName_Scenario_Name',
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
    grouped_requests = {}
    transaction_index = 1
    last_time = None
    group_name = f'Transaction_{transaction_index}'
    grouped_requests[group_name] = []

    for entry in entries:
        startedDateTime = entry.get('startedDateTime')
        if startedDateTime:
            try:
                current_time = datetime.strptime(startedDateTime, '%Y-%m-%dT%H:%M:%S.%fZ')
            except ValueError:
                current_time = datetime.strptime(startedDateTime, '%Y-%m-%dT%H:%M:%SZ')
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
            'testname': f'S{str(idx).zfill(2)}_{group_name}',
            'enabled': 'true'
        })
        SubElement(transaction_controller, 'boolProp', {'name': 'TransactionController.includeTimers'}).text = 'false'
        transaction_hash_tree = SubElement(thread_hash_tree, 'hashTree')


        #for entry in group_entries:
        for request_index, entry in enumerate(grouped_requests, start=1):
            request = entry['request']
            url = request['url']
            method = request['method']
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
            sampler_name = f'T{idx:02d}{request_index:02d}_{method}_{base_name}'    

            http_sampler = SubElement(transaction_hash_tree, 'HTTPSamplerProxy', {
                'guiclass': 'HttpTestSampleGui',
                'testclass': 'HTTPSamplerProxy',
                'testname': sampler_name,
                'enabled': 'true'
            })
            SubElement(http_sampler, 'stringProp', {'name': 'HTTPSampler.domain'}).text = domain
            SubElement(http_sampler, 'stringProp', {'name': 'HTTPSampler.protocol'}).text = protocol
            SubElement(http_sampler, 'stringProp', {'name': 'HTTPSampler.port'}).text = port
            SubElement(http_sampler, 'stringProp', {'name': 'HTTPSampler.path'}).text = path
            SubElement(http_sampler, 'stringProp', {'name': 'HTTPSampler.method'}).text = method

            #Added missing standard properties
            SubElement(http_sampler, 'stringProp', {'name': 'HTTPSampler.contentEncoding'}).text = 'UTF-8'
            SubElement(http_sampler, 'boolProp', {'name': 'HTTPSampler.follow_redirects'}).text = 'false'
            SubElement(http_sampler, 'boolProp', {'name': 'HTTPSampler.auto_redirects'}).text = 'false'
            SubElement(http_sampler, 'boolProp', {'name': 'HTTPSampler.use_keepalive'}).text = 'true'
            SubElement(http_sampler, 'boolProp', {'name': 'HTTPSampler.DO_MULTIPART_POST'}).text = 'false'
            SubElement(http_sampler, 'stringProp', {'name': 'HTTPSampler.embedded_url_re'}).text = ''


            # Handle GET Parameters
            if method == 'GET':
                #parse URL
                parsed_url = urlparse(url)

                #Set path without query string
                SubElement(http_sampler, 'stringProp', {'name': 'HTTPSampler.path'}).text = parsed_url.path

                # Merge query params from parsed URL and HAR queryString
                query_params_combined = {}

                # From parsed URL
                for name, values in parse_qs(parsed_url.query, keep_blank_values=True).items():
                    query_params_combined.setdefault(name, []).extend(values)

                # from har queryString
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
                            SubElement(param_element, 'stringProp', {'name': 'Argument.name'}).text = name
                            SubElement(param_element, 'stringProp', {'name': 'Argument.value'}).text = value
                            SubElement(param_element, 'stringProp', {'name': 'Argument.metadata'}).text = '='
                            SubElement(param_element, 'boolProp', {'name': 'HTTPArgument.use_equals'}).text = 'true'

            
            #handle POST Method
            if method == 'POST':
                parsed_url = urlparse(url)

                #detect if body is JSON or form params
                has_params = 'params' in request.get('postData', {})
                has_text = 'text' in request.get('postData', {})

                #Create Aruguments block
                args_prop = SubElement(http_sampler, 'elementProp', {
                    'name': 'HTTPsampler.Arguments',
                    'elementType': 'Arguments',
                    'guiclass': 'HTTPArgumentsPanel',
                    'testclass': 'Arguments',
                    'testname': 'User Defined Variables',
                    'enabled': 'true'
                })
                collection_prod = SubElement(args_prop, 'collectionProp', {'name': 'Arguments.arguments'})

                if has_params:
                    # Form-Style POST: strip query from path
                    SubElement(http_sampler, 'stringProp', {'name': 'HTTPSampler.path'}).text = parsed_url.path
                    SubElement(http_sampler, 'stringProp', {'name': 'HTTPSampler.postBodyRaw'}).text = 'false'

                    for param in request['postData']['params']:
                        param_element = SubElement(collection_prod, 'elementProp', {
                            'name': param['name'],
                            'elementType': 'HTTPArgument'
                        })
                        SubElement(param_element, 'boolProp', {'name': 'HTTPArgument.always_encode'}).text = 'false'
                        SubElement(param_element, 'stringProp', {'name': 'Argument.name'}).text = param['name']
                        SubElement(param_element, 'stringProp', {'name': 'Argument.value'}).text = param.get('value', '')
                        SubElement(param_element, 'stringProp', {'name': 'Argument.metadata'}).text = '='
                        SubElement(param_element, 'boolProp', {'name': 'HTTPArgument.use_equals'}).text = 'true'

                elif has_text:
                    #JSON Body POST: Keep query in Path
                    full_path = parsed_url.path
                    if parsed_url.query:
                        full_path += '?' + parsed_url.query
                    SubElement(http_sampler, 'stringProp', {'name': 'HTTPSampler.path'}).text = full_path
                    SubElement(http_sampler, 'boolProp', {'name': 'HTTPSampler.postBodyRaw'}).text = 'true'

                    param_element = SubElement(collection_prod, 'elementProp', {
                        'name': '',
                        'elementType': 'HTTPArgument'
                    })
                    SubElement(param_element, 'boolProp', {'name': 'HTTPArgument.always_encode'}).text = 'false'
                    #SubElement(param_element, 'stringProp', {'name': 'Argument.name'}).text = ''
                    SubElement(param_element, 'stringProp', {'name': 'Argument.value'}).text = request['postData']['text']
                    SubElement(param_element, 'stringProp', {'name': 'Argument.metadata'}).text = '='
                    SubElement(param_element, 'boolProp', {'name': 'HTTPArgument.use_equals'}).text = 'true'

            
            #Add File upload part for POST request
            if method == 'POST' and 'params' in request.get('postData', {}):
                args_prop = SubElement(http_sampler, 'elementProp', {
                    'name': 'HTTPsampler.Arguments',
                    'elementType': 'Arguments',
                    'guiclass': 'HTTPArgumentsPanel',
                    'testclass': 'Arguments',
                    'testname': 'User Defined Variables',
                    'enabled': 'true'
                })
                collection_prod = SubElement(args_prop, 'collectionProp', {'name': 'Arguments.arguments'})

                for param in request['postData']['params']:
                    param_element = SubElement(collection_prod, 'elementProp', {
                        'name': param.get('name', ''),
                        'elementType': 'HTTPArgument'
                    })
                    SubElement(param_element, 'boolProp', {'name': 'HTTPArgument.always_encode'}).text = 'false'
                    SubElement(param_element, 'stringProp', {'name': 'Argument.name'}).text = param.get('name', '')
                    SubElement(param_element, 'stringProp', {'name': 'Argument.value'}).text = param.get('filename', param.get('value', ''))
                    SubElement(param_element, 'stringProp', {'name': 'Argument.metadata'}).text = '='
                    SubElement(param_element, 'boolProp', {'name': 'HTTPArgument.use_equals'}).text = 'true'

            #Add hasTree for HTTP Sampler
            sampler_hash_tree = SubElement(transaction_hash_tree, 'hashTree')

            #Add Header Manager
            header_manager = SubElement(sampler_hash_tree, 'HeaderManager', {
                'guiclass': 'HeaderPanel',
                'testclass': 'HeaderManager',
                'testname':  'HTTP Header Manager',
                'enabled': 'true'
            })
            collection_prop = SubElement(header_manager, 'collectionProp', {'name': 'HeaderManager.headers'})
            for header in request.get('headers', []):
                #Skip HTTP/2 pseudo headers
                if header['name'].startswith(':'):
                    continue
                header_element = SubElement(collection_prop, 'elementProp', {
                    'name': header['name'],
                    'elementType': 'Header'
                })
                SubElement(header_element, 'stringProp', {'name': 'Header.name'}).text = header['name']
                SubElement(header_element, 'stringProp', {'name': 'Header.value'}).text = header['value']
            
            SubElement(sampler_hash_tree, 'hashTree')
    
    if include_listeners:
        add_listener_config(thread_hash_tree)

    if include_sampler:
        add_debug_sampler(thread_hash_tree)

    xml_str = tostring(jmeter_test_plan, 'utf-8')
    pretty_xml = parseString(xml_str).toprettyxml(indent="  ")
    return pretty_xml


#Streamlit App
def main():
    

    st.title("HAR to JMX Converter")
    st.write("Upload a **.har** file to generate a standardized **.jmx (JMeter)** file 🚀🎯😊. After conversion, you can proceed with further script enhancements. \n\n **Note:** Please upload only one file at a time. We do not store any uploaded files on our server. Simply upload and export instantly.")
    st.write("This tool is designed to save you time! I hope you find it helpful. Please feel free to message me, if you have any issue or suggestions.")

    uploaded_file = st.file_uploader("Choose a recorded HAR file", type="har")

    st.subheader("Transaction controller grouped by a time gap")
    time_gap = st.slider("Time Gap Threshold (seconds)", min_value=1, max_value=15, value=5)

    #thread_group_name = st.text_input("Thread Group Name", value="S01_ProjectName_Scenario_Name")

    st.subheader("Optional Configuration Toggles")
    include_headers = st.toggle("Header Configuraiton (Cache, Cookie, Request Defaults)", value=False)
    include_listeners = st.toggle("Listeners Configuration (View Results Tree, Summary Report, Aggregate Report)", value=False)
    include_sampler = st.toggle("Sampler Configuration (Debug Sampler)", value=False)


    if st.button("Convert to JMX"):
        if uploaded_file is None:
            st.error("Upload file and then try again. Refresh the screen!!")
        else:
            with st.spinner("Converting..."):
                har_content = json.load(uploaded_file)
                jmx_content = har_to_jmx(har_content,
                                         time_gap_threshold=time_gap,
                                         include_headers=include_headers,
                                         include_listeners=include_listeners,
                                         include_sampler=include_sampler)
                original_name = os.path.splitext(uploaded_file.name)[0]
                output_filename = f"{original_name}_Converted_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jmx"

                st.download_button(
                    label="Download JMX File",
                    data=jmx_content,
                    file_name=output_filename,
                    mime="application/xml"
                )

                st.success(f"Conversion Completed! Click on the \"Download JMX File\" button above to download your file. **{output_filename}**")

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
        st.write("I will be updating more points soon...")


    



if __name__ == "__main__":
    main()
    
                    