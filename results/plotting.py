import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path


# figures variables
SMALL_SIZE = 20
MEDIUM_SIZE = 32
LARGE_SIZE = 32
#plt.rc('font', size=SMALL_SIZE, family='Times New Roman')
plt.rc('font', size=SMALL_SIZE)
plt.rc('axes', titlesize=MEDIUM_SIZE)
plt.rc('axes', labelsize=MEDIUM_SIZE)
plt.rc('axes', linewidth=2.0)
plt.rc('xtick', labelsize=28)
plt.rc('ytick', labelsize=SMALL_SIZE)
plt.rc('legend', fontsize=SMALL_SIZE)
plt.rc('figure', titlesize=LARGE_SIZE)


# plots all metrics in one graph
def _plot_all_metrics(parameters):
    experiment = parameters['experiment']
    results_file = parameters['results_file']
    services = parameters['services']
    fig, axs = plt.subplots(len(services), 3, figsize=(25, 25), sharex=False)
    results = pd.read_csv(results_file)
    index = 0
    for services_number in services:
        filtered_results = results.loc[results['services'] == services_number]
        if len(results) > 0:
            sns.barplot(x='approach', y='total_time', hue='length', data=filtered_results, ax=axs[index][0])
            axs[index][0].set(title=('Average Response Time'))
            axs[index][0].set(xlabel=('Approach'))
            axs[index][0].set(ylabel=('Milliseconds (ms)'))
            axs[index][0].grid(linestyle='-', linewidth='1.0', color='grey')
            handles, labels = axs[index][0].get_legend_handles_labels()
            axs[index][0].legend(handles, labels, title='Composition\nLength')

            sns.barplot(x='approach', y='messages_size', hue='length', data=filtered_results, ax=axs[index][1])
            axs[index][1].set(title=('Average Messages Size'))
            axs[index][1].set(xlabel=('Approach'))
            axs[index][1].set(ylabel=('Bytes'))
            axs[index][1].grid(linestyle='-', linewidth='1.0', color='grey')
            handles, labels = axs[index][1].get_legend_handles_labels()
            axs[index][1].legend(handles, labels, title='Composition\nLength')

            sns.barplot(x='approach', y='input_size', hue='length', data=filtered_results, ax=axs[index][2])
            axs[index][2].set(title=('Average Input Size'))
            axs[index][2].set(xlabel=('Approach'))
            axs[index][2].set(ylabel=('Bytes'))
            axs[index][2].grid(linestyle='-', linewidth='1.0', color='grey')
            handles, labels = axs[index][2].get_legend_handles_labels()
            axs[index][2].legend(handles, labels, title='Composition\nLength')
        index = index + 1
    fig.tight_layout(rect=[0, 0.03, 1, 0.95])
    fig.savefig('./results/figs/' + experiment + '/all-results.pdf')


# plots a graph per each experiment with different services
def _plot_services(parameters):
    experiment = parameters['experiment']
    results_file = parameters['results_file']
    services = parameters['services']
    results = pd.read_csv(results_file)
    index = 0
    for services_number in services:
        filtered_results = results.loc[results['services'] == services_number]
        fig, axs = plt.subplots(1, 3, figsize=(25, 25), sharex=False)
        if len(results) > 0:
            sns.barplot(x='approach', y='total_time', hue='length', data=filtered_results, ax=axs[0])
            axs[0].set(title=('Average Response Time'))
            axs[0].set(xlabel=('Approach'))
            axs[0].set(ylabel=('Milliseconds (ms)'))
            axs[0].grid(linestyle='-', linewidth='1.0', color='grey')
            handles, labels = axs[0].get_legend_handles_labels()
            axs[0].legend(handles, labels, title='Composition\nLength')

            sns.barplot(x='approach', y='messages_size', hue='length', data=filtered_results, ax=axs[1])
            axs[1].set(title=('Average Messages Size'))
            axs[1].set(xlabel=('Approach'))
            axs[1].set(ylabel=('Bytes'))
            axs[1].grid(linestyle='-', linewidth='1.0', color='grey')
            handles, labels = axs[1].get_legend_handles_labels()
            axs[1].legend(handles, labels, title='Composition\nLength')

            sns.barplot(x='approach', y='input_size', hue='length', data=filtered_results, ax=axs[2])
            axs[2].set(title=('Average Input Size'))
            axs[2].set(xlabel=('Approach'))
            axs[2].set(ylabel=('Bytes'))
            axs[2].grid(linestyle='-', linewidth='1.0', color='grey')
            handles, labels = axs[2].get_legend_handles_labels()
            axs[2].legend(handles, labels, title='Composition\nLength')
        fig.tight_layout(rect=[0, 0.03, 1, 0.95])
        fig.savefig('./results/figs/' + experiment + '/' + str(services_number) + '-services-results.pdf')


# plots experiment results
def plot_results(parameters):
    experiment = parameters['experiment']
    Path('./results/figs/' + experiment).mkdir(parents=True, exist_ok=True)
    _plot_all_metrics(parameters)
    _plot_services(parameters)
