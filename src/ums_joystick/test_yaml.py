import yaml

doc = yaml.load(open('../../param/variables.yaml', 'r'))
print(doc)

def get_configs(key,data):
    if key in data.keys():
        return data[key] 

print("ACCEL_MAX : {}".format(get_configs('ACCEL_MAX', doc)))
print("APS_VAL : {}".format(get_configs('APS_VAL', doc)))
print("DELTA_MINUS : {}".format(get_configs('DELTA_MINUS', doc)))
print("DELTA_PLUS : {}".format(get_configs('DELTA_PLUS', doc)))
print("STEER_LIMIT : {}".format(get_configs('STEER_LIMIT', doc)))
print("STEER_RATIO : {}".format(get_configs('STEER_RATIO', doc)))