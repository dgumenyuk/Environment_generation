'''
Module to illustrate the created scenarios
'''


import numpy as np
import matplotlib.pyplot as plt
import time


class ImageBuilder:
    def __init__(self, folder, duration, smpl_rate):
        self.folder = folder
        self.duration = duration
        self.smpl_rate = smpl_rate

    def build_image(
        self,
        option,
        tc_id,
        fitness,
        ss_tmp=[],
        id_tmp=[],
    ):
        fig, ax1 = plt.subplots(figsize=(24, 8))

        if option == 1:
            ax1.set_title(
                "Temperature values expected" + ", smpl_rate = " + str(self.smpl_rate),
                fontsize=17,
            )

            ax1.plot(
                [i * 3 / 60 * self.smpl_rate for i in range(0, len(id_tmp))],
                id_tmp,
                "o--b",
                label="Scheduled temperature",
            )
            plt.xticks(np.arange(0, len(id_tmp) * 3 / 60 * self.smpl_rate + 1, step=2))
        elif option == 2:
            ax1.set_title(
                "Temperature values simulated" + ", smpl_rate = " + str(self.smpl_rate),
                fontsize=17,
            )

            ax1.plot(
                [i * 3 / 60 * self.smpl_rate for i in range(0, len(ss_tmp))],
                ss_tmp,
                "or",
                label="Actual temperature",
            )
            plt.xticks(np.arange(0, len(ss_tmp) * 3 / 60 * self.smpl_rate + 1, step=2))
        elif option == 3:
            ax1.set_title(
                "Temperature values expected vs simulated, fitness = "
                + str(fitness)
                + ", smpl_rate = "
                + str(self.smpl_rate),
                fontsize=17,
            )

            ax1.plot(
                [i * 3 / 60 * self.smpl_rate for i in range(0, len(id_tmp))],
                id_tmp,
                "o--b",
                label="Scheduled temperature",
            )

            ax1.plot(
                [i * 3 / 60 * self.smpl_rate for i in range(0, len(ss_tmp))],
                ss_tmp,
                "or",
                label="Actual temperature",
            )

            plt.xticks(np.arange(0, len(ss_tmp) * 3 / 60 * self.smpl_rate + 1, step=2))

        ax1.set_xlabel("Time, hours", fontsize=14)
        ax1.set_ylabel("Temperature value in degrees Celsius", fontsize=14)
        top = 28
        bottom = 15
        ax1.set_ylim(bottom, top)

        plt.yticks(np.arange(bottom, top + 1, 1.0), fontsize=12)

        plt.grid(b=True, which="major", axis="both")

        ax1.legend(fontsize=14)
        ctime = int(time.time())

        fig.savefig(self.folder + "\\" + str(tc_id) + ".png")
        plt.close(fig)
