import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


# figures variables
SMALL_SIZE = 20
MEDIUM_SIZE = 32
LARGE_SIZE = 32
plt.rc('font', size=SMALL_SIZE, family='Times New Roman')
plt.rc('axes', titlesize=MEDIUM_SIZE)
plt.rc('axes', labelsize=MEDIUM_SIZE)
plt.rc('axes', linewidth=2.0)
plt.rc('xtick', labelsize=28)
plt.rc('ytick', labelsize=SMALL_SIZE)
plt.rc('legend', fontsize=SMALL_SIZE)
plt.rc('figure', titlesize=LARGE_SIZE)


# plots experiment results
def plot_results(parameters):
    experiment = parameters['experiment']
    results_file = parameters['results_file']
    services = parameters['services']
    fig, axs = plt.subplots(3, len(services), figsize=(10, 10), sharex=False)
    results = pd.read_csv(results_file)
    index = 0
    for services_number in services:
        results = results.loc[results['services'] == services_number]

        sns.barplot(x='approach', y='total_time', hue='length', data=results, ax=axs[0][index])
        axs[0][index].set(title=('Average Response Time'))
        axs[0][index].set(xlabel=('Approach'))
        axs[0][index].set(ylabel=('Milliseconds (ms)'))
        axs[0][index].grid(linestyle='-', linewidth='1.0', color='grey')
        handles, labels = axs[0][index].get_legend_handles_labels()
        axs[0][index].legend(handles, labels, title='Composition\nLength')

        sns.barplot(x='approach', y='messages_size', hue='length', data=results, ax=axs[1][index])
        axs[1][index].set(title=('Average Messages Size'))
        axs[1][index].set(xlabel=('Approach'))
        axs[1][index].set(ylabel=('Bytes'))
        axs[1][index].grid(linestyle='-', linewidth='1.0', color='grey')
        handles, labels = axs[1][index].get_legend_handles_labels()
        axs[1][index].legend(handles, labels, title='Composition\nLength')

        sns.barplot(x='approach', y='input_size', hue='length', data=results, ax=axs[2][index])
        axs[2][index].set(title=('Average Input Size'))
        axs[2][index].set(xlabel=('Approach'))
        axs[2][index].set(ylabel=('Bytes'))
        axs[2][index].grid(linestyle='-', linewidth='1.0', color='grey')
        handles, labels = axs[2][index].get_legend_handles_labels()
        axs[2][index].legend(handles, labels, title='Composition\nLength')

        fig.tight_layout(rect=[0, 0.03, 1, 0.95])
        fig.savefig('./results/figs/results_' + experiment + '.pdf')