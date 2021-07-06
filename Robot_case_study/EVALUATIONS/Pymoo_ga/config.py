ga = {"population": 100, "n_gen": 400, "seed": 873, "mut_rate": 0.4, "cross_rate": 1}

model = {
    "map_size": 50,
    "min_len": 5,  # minimal possible distance in meters
    "max_len": 15,  # maximal possible disance to go straight in meters
    "len_step": 1,  # y axis step
    "pos_step": 1,  # x axis step
}

files = {
    "ga_archive": ".\\GA_archive\\",  # folder to save the results history
    "ga_conv": ".\\",
    "schedules": "roads.json",
    "models": "models.csv",
    "tc_img": ".\\TC_img\\",  # folder to save the illustrations for the test cases
    "tc_file": ".\\TC_file\\",  # folder to save the specifications for the scenarios
}
