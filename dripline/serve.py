import yaml
import dripline

with open( "../examples/kv_store_tutorial.yaml", "r" ) as stream:
    
    try:
        store = yaml.safe_load( stream )
        print ( yaml.dump(store) )
        
    except yaml.YAMLError as exc:
        print( exc )
        
#file_name = file( "../examples/kv_store_tutorial.yaml", "r" )
#print yaml.dump( yaml.load(file_name), default_flow_style=False )

