ga = {
    "population": 90,
    "n_gen": 200,
    "seed": 879533,
    "mut_rate": 0.4,
    "cross_rate": 1
} 

model = {
    "speed": 9,
    "map_size": 200,
    "steer_ang": 12,
    "min_len": 5,  # minimal possible distance in meters
    "max_len": 30,  # maximal possible disance to go straight in meters
    "min_angle": 10,  # minimal angle of rotation in degrees
    "max_angle":  85 # maximal angle of rotation in degrees
}

files = {
    #"ga_conv": ".\\ResGA\\",
    "ga_archive": ".\\GA_archive\\",
    "ga_conv": ".\\",
    "schedules": "roads.json",
    "models": "models.csv",
    #"tc_img": ".\\ImgGA\\",
    #"tc_folder": ".\\TCs\\"
    "tc_img": ".\\TC_img\\",
    "tc_file": ".\\TC_file\\"
}
