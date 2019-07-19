import yaml
import scarab
import dripline

with open( "../examples/kv_store_tutorial.yaml", "r" ) as stream:
    
    try:
        store = yaml.safe_load( stream )
        
        for key, value in store.items():
            
            if( key == "module" and value == "Service" ):
                
                service = dripline.core.Service()
                print( "created new service with default parameters" )
                
            elif( key == "endpoints" ):
                
                for sub_key in value:
                    service.add_child( dripline.core._Endpoint(sub_key.get("name")) )

    except yaml.YAMLError as exc:
        print( exc )
        
#file_name = file( "../examples/kv_store_tutorial.yaml", "r" )
#print yaml.dump( yaml.load(file_name), default_flow_style=False )

