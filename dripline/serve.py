import yaml
  
file_name = file( "../examples/kv_store_tutorial.yaml", "r" )
#print yaml.dump( yaml.load(file_name), default_flow_style=False )

for data in yaml.load(file_name):
    print data
    print "-----------------------------------------"
