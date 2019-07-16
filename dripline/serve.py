import ruamel.yaml
import dripline

with open( "../examples/kv_store_tutorial.yaml", "r" ) as stream:
    
    try:
        store = ruamel.yaml.safe_load( stream, Loader = ruamel.yaml.RoundTripLoader )
        print ( ruamel.yaml.dump(store, Dumper = ruamel.yaml.RoundTripDumper) )
        
    except ruamel.yaml.YAMLError as exc:
        print( exc )
        
#file_name = file( "../examples/kv_store_tutorial.yaml", "r" )
#print yaml.dump( yaml.load(file_name), default_flow_style=False )

