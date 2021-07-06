ga = {"population": 250, "n_gen": 200, "seed": 494948, "mut_rate": 0.4, "cross_rate": 1}

# seed 896

model = {
    "speed": 9,
    "map_size": 200,
    "steer_ang": 12,
    "min_len": 5,  # minimal possible distance in meters
    "max_len": 50,  # maximal possible disance to go straight in meters
    "min_angle": 10,  # minimal angle of rotation in degrees
    "max_angle": 85,  # maximal angle of rotation in degrees
    "ang_step": 5,
    "len_step": 1,
}

files = {
    # "ga_conv": ".\\ResGA\\",
    "ga_archive": ".\\GA_archive\\",
    "ga_conv": ".\\",
    "schedules": "roads.json",
    "models": "models.csv",
    # "tc_img": ".\\ImgGA\\",
    # "tc_folder": ".\\TCs\\"
    "tc_img": ".\\TC_img\\",
    "tc_file": ".\\TC_file\\",
}
