import yaml
import scarab
import dripline
from endpoint import Endpoint

def add_endpoints( this_service, this_endpoint_list ):
    for an_endpoint in this_endpoint_list:
        module = an_endpoint.pop( "module" )
        if module in globals():
            new_endpoint = globals()[module](**an_endpoint)
            this_service.add_child( new_endpoint )
            #print( "Added endpoint " + new_endpoint.get_name() + " as a child to service" )

with open( "../examples/kv_store_tutorial.yaml", "r" ) as stream:

    store = yaml.safe_load( stream )
    
    if "module" not in store:
        service = dripline.core.Service()
        print( "No service module found, creating new service with default parameters" )
        
    else:
        module = store.pop( "module" )
        # This service is meant to be used when the yaml file speficies more details about the service
        service = dripline.core.Service()

    endpoint_list = store.pop( "endpoints", [] )
    add_endpoints( service, endpoint_list )
        
    endpoint_dict = service.sync_children()
    request = dripline.core.MsgRequest().create()
    print( "Routing key: " + request.get_routing_key() )

    if request.get_routing_key() in endpoint_dict:
        print( endpoint_dict.get(request.get_routing_key()).submit_request_message(request) )
    
    #print( endpoint_dict.get("peaches").submit_request_message(request) )
    #service.start()
    #service.listen()
