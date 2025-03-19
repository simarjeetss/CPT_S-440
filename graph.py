import os
import pickle
import matplotlib.pyplot as plt


class Graph:

    def __init__(self, model_name, opponent="all"):
        self.model_name = model_name
        self.opponent = opponent
        self.filepath_evaluation_scores = ""
        self.filepath_graph = ""
        self.filepath_graph_checkpoint = ""

    def load_evaluation_scores(self):
        with open(self.filepath_evaluation_scores, "rb") as file_handler:
            return pickle.load(file_handler)


    def show(self):
        plt.show()

    def save(self, checkpoint=False):
        path = self.filepath_graph_checkpoint if checkpoint else self.filepath_graph
        try:
            plt.savefig(path)
        except:
            pass
        plt.clf()

    def open_saved_figure(self, from_checkpoint=False):
        path = self.filepath_graph_checkpoint if from_checkpoint else self.filepath_graph
        if os.path.exists(path):
            os.startfile(path)
        else:
            print("file does not exist")
