import pandas as pd
pd.options.mode.chained_assignment = None
import seaborn as sns
import matplotlib.pyplot as plt
import networkx as nx
from pathlib import Path


# figures variables
SMALL_SIZE = 20
MEDIUM_SIZE = 32
LARGE_SIZE = 32
plt.rc('font', size=SMALL_SIZE, family='Times New Roman')
plt.rc('font', size=SMALL_SIZE)
plt.rc('axes', titlesize=MEDIUM_SIZE)
plt.rc('axes', labelsize=MEDIUM_SIZE)
plt.rc('axes', linewidth=2.0)
plt.rc('xtick', labelsize=28)
plt.rc('ytick', labelsize=SMALL_SIZE)
plt.rc('legend', fontsize=SMALL_SIZE)
plt.rc('figure', titlesize=LARGE_SIZE)
sns.set_palette("Paired")


# plots experiment results
def plot_results(parameters):
    experiment = parameters['experiment']
    Path('./results/figs/' + experiment).mkdir(parents=True, exist_ok=True)
    _plot_all_metrics(parameters)
    _plot_services(parameters)
    _plot_metrics(parameters)


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
            sns.barplot(x='approach', y='execution_time', hue='length', data=filtered_results, ax=axs[index][0], errorbar=None)
            axs[index][0].set(title=('Average Response Time'))
            axs[index][0].set(xlabel=('Approach'))
            axs[index][0].set(ylabel=('Milliseconds (ms)'))
            axs[index][0].grid(linestyle='-', linewidth='1.0', color='grey')
            handles, labels = axs[index][0].get_legend_handles_labels()
            axs[index][0].legend(handles, labels, title='Graph Size')

            filtered_results['messages_size'] = filtered_results['messages_size'] / 1024
            sns.barplot(x='approach', y='messages_size', hue='length', data=filtered_results, ax=axs[index][1])
            axs[index][1].set(title=('Average Messages Size'))
            axs[index][1].set(xlabel=('Approach'))
            axs[index][1].set(ylabel=('Bytes'))
            axs[index][1].grid(linestyle='-', linewidth='1.0', color='grey')
            handles, labels = axs[index][1].get_legend_handles_labels()
            axs[index][1].legend(handles, labels, title='Graph Size')

            filtered_results['input_size'] = filtered_results['input_size'] / 1024
            sns.barplot(x='approach', y='input_size', hue='length', data=filtered_results, ax=axs[index][2])
            axs[index][2].set(title=('Average Input Size'))
            axs[index][2].set(xlabel=('Approach'))
            axs[index][2].set(ylabel=('Bytes'))
            axs[index][2].grid(linestyle='-', linewidth='1.0', color='grey')
            handles, labels = axs[index][2].get_legend_handles_labels()
            axs[index][2].legend(handles, labels, title='Graph Size')
        index = index + 1
    fig.tight_layout(rect=[0, 0.03, 1, 0.95])
    fig.savefig('./results/figs/' + experiment + '/all-results.pdf')


# plots a graph per each experiment with different services
def _plot_services(parameters):
    experiment = parameters['experiment']
    results_file = parameters['results_file']
    services = parameters['services']
    results = pd.read_csv(results_file)
    for services_number in services:
        filtered_results = results.loc[results['services'] == services_number]
        fig, axs = plt.subplots(1, 3, figsize=(25, 10), sharex=False)
        if len(results) > 0:
            sns.barplot(x='approach', y='total_time', hue='length', data=filtered_results, ax=axs[0])
            sns.barplot(x='approach', y='execution_time', hue='length', data=filtered_results, ax=axs[0], errorbar=None)
            axs[0].set(title=('Average Response Time'))
            axs[0].set(xlabel=('Approach'))
            axs[0].set(ylabel=('Milliseconds (ms)'))
            axs[0].grid(linestyle='-', linewidth='1.0', color='grey')
            handles, labels = axs[0].get_legend_handles_labels()
            axs[0].legend(handles, labels, title='Graph Size')

            filtered_results['messages_size'] = filtered_results['messages_size'] / 1024
            sns.barplot(x='approach', y='messages_size', hue='length', data=filtered_results, ax=axs[1])
            axs[1].set(title=('Average Messages Size'))
            axs[1].set(xlabel=('Approach'))
            axs[1].set(ylabel=('Bytes'))
            axs[1].grid(linestyle='-', linewidth='1.0', color='grey')
            handles, labels = axs[1].get_legend_handles_labels()
            axs[1].legend(handles, labels, title='Graph Size')

            filtered_results['input_size'] = filtered_results['input_size'] / 1024
            sns.barplot(x='approach', y='input_size', hue='length', data=filtered_results, ax=axs[2])
            axs[2].set(title=('Average Input Size'))
            axs[2].set(xlabel=('Approach'))
            axs[2].set(ylabel=('Bytes'))
            axs[2].grid(linestyle='-', linewidth='1.0', color='grey')
            handles, labels = axs[2].get_legend_handles_labels()
            axs[2].legend(handles, labels, title='Graph Size')
        fig.tight_layout(rect=[0, 0.03, 1, 0.95])
        fig.savefig('./results/figs/' + experiment + '/' + str(services_number) + '-services-results.pdf')


# plots a graph per each experiment with different services
def _plot_metrics(parameters):
    experiment = parameters['experiment']
    results_file = parameters['results_file']
    services = parameters['services']
    lengths = parameters['lengths']
    results = pd.read_csv(results_file)
    metrics = ['response-time', 'execution-time', 'planning-time']
    approaches = []
    for approach in parameters['approaches']:
        if approach == 'doa':
            approaches.append('Data-oriented')
        if approach == 'conversation':
            approaches.append('Conversation')
        if approach == 'planning':
            approaches.append('Planning')
    for metric in metrics:
        index1 = 0
        index2 = 0
        fig, axs = plt.subplots(2, 2, figsize=(25, 25), sharex=False, sharey=False)
        for services_number in services:
            if services_number == 1000:
                index1 = 0
                index2 = 1
            if services_number == 10000:
                index1 = 1
                index2 = 0
            if services_number == 100000:
                index1 = 1
                index2 = 1
            filtered_results = results.loc[results['services'] == services_number]
            if metric == 'response-time':
                g = sns.barplot(x='approach', y='total_time', hue='length', data=filtered_results, errorbar='sd', ax=axs[index1][index2])
                axs[index1][index2].set(title=(str(services_number) + ' services in registry'))
                g.set_xticklabels(approaches)
                axs[index1][index2].set(xlabel=('Approach'))
                axs[index1][index2].set(ylabel=('Milliseconds (ms)'))
                handles, labels = axs[index1][index2].get_legend_handles_labels()
                axs[index1][index2].legend(handles, labels, title='Graph Size')
                axs[index1][index2].grid(linestyle='-', linewidth=0.5, alpha=0.25, axis='both', color='grey')
            if metric == 'execution-time':
                g = sns.barplot(x='approach', y='execution_time', hue='length', data=filtered_results, errorbar='sd', ax=axs[index1][index2])
                axs[index1][index2].set(title=(str(services_number) + ' services in registry'))
                g.set_xticklabels(approaches)
                axs[index1][index2].set(xlabel=('Approach'))
                axs[index1][index2].set(ylabel=('Milliseconds (ms)'))
                handles, labels = axs[index1][index2].get_legend_handles_labels()
                axs[index1][index2].legend(handles, labels, title='Graph Size')
                axs[index1][index2].grid(linestyle='-', linewidth=0.5, alpha=0.25, axis='both', color='grey')
            if metric == 'planning-time':
                g = sns.barplot(x='approach', y='planning_time', hue='length', data=filtered_results, errorbar='sd', ax=axs[index1][index2])
                axs[index1][index2].set(title=(str(services_number) + ' services in registry'))
                g.set_xticklabels(approaches)
                axs[index1][index2].set(xlabel=('Approach'))
                axs[index1][index2].set(ylabel=('Milliseconds (ms)'))
                handles, labels = axs[index1][index2].get_legend_handles_labels()
                axs[index1][index2].legend(handles, labels, title='Graph Size')
                axs[index1][index2].grid(linestyle='-', linewidth=0.5, alpha=0.25, axis='both', color='grey')
        fig.savefig('./results/figs/' + experiment + '/' + metric + '-services-results.pdf')

    metrics = ['messages-size', 'input-size']
    for metric in metrics:
        index1 = 0
        index2 = 0
        fig, axs = plt.subplots(2, 2, figsize=(25, 25), sharex=False, sharey=False)
        for length in lengths:
            if length == 10:
                index1 = 0
                index2 = 1
            if length == 15:
                index1 = 1
                index2 = 0
            if length == 20:
                index1 = 1
                index2 = 1
            colors = []
            if metric == 'messages-size':
                filtered_results = results.loc[results['services'] == 100000]
                filtered_results = filtered_results.loc[filtered_results['length'] == length]
                filtered_results['messages_size'] = filtered_results['messages_size']/1024
                g = sns.barplot(x="approach", y='messages_size', data=filtered_results, errorbar='sd', ax=axs[index1][index2])
                axs[index1][index2].set(title=('Composition graphs of size ' + str(length)))
                g.set_xticklabels(approaches)
                axs[index1][index2].set(xlabel=('Approach'))
                axs[index1][index2].set(ylabel=('Kilobytes (KBs)'))
                axs[index1][index2].legend([], [], frameon=False)
                axs[index1][index2].grid(linestyle='-', linewidth=0.5, alpha=0.25, axis='both', color='grey')
            if metric == 'input-size':
                filtered_results = results.loc[results['services'] == 100000]
                filtered_results = filtered_results.loc[filtered_results['length'] == length]
                filtered_results['input_size'] = filtered_results['input_size'] / 1024
                g = sns.barplot(x='approach', y='input_size', data=filtered_results, errorbar='sd', ax=axs[index1][index2])
                axs[index1][index2].set(title=('Composition graphs of size ' + str(length)))
                g.set_xticklabels(approaches)
                axs[index1][index2].set(xlabel=('Approach'))
                axs[index1][index2].set(ylabel=('Kilobytes (KBs)'))
                axs[index1][index2].legend([], [], frameon=False)
                axs[index1][index2].grid(linestyle='-', linewidth=0.5, alpha=0.25, axis='both', color='grey')
        fig.savefig('./results/figs/' + experiment + '/' + metric + '-services-results.pdf')


# plots graph
def plot_graph(path, graph):
    nx.draw(graph)
    plt.savefig(path, format="png")
    plt.clf()
