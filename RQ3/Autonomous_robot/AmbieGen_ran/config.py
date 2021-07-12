ga = {"population": 30, "n_gen": 45, "seed": 873, "mut_rate": 0.4, "cross_rate": 1}

model = {
    "map_size": 50,
    "min_len": 5,  # minimal possible distance in meters
    "max_len": 15,  # maximal possible disance to go straight in meters
    "len_step": 1,
    "pos_step": 1,
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
