import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


def plot_results(path):
    results = pd.read_csv(path)
    sns.barplot(x='', y='', hue='', data=results)
    plt.show()