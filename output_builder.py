import pandas as pd
import seaborn as sns
from datetime import date
import matplotlib.pyplot as plt
from polls_extractor import CnnTracker, RcpTracker

if __name__ == '__main__':

    ## URLs
    cnn_tracker = CnnTracker('https://www.cnn.com/election/2020/presidential-polls/')
    rcp_tracker = RcpTracker('https://www.realclearpolitics.com/epolls/2020/president/us/general_election_trump_vs_biden-6247.html')

    ## Poll Data
    cnn_data = cnn_tracker.poll_tracker()
    rcp_data = rcp_tracker.poll_tracker()

    ## Average Poll Numbers by Date
    union_df = pd.concat([cnn_data, rcp_data])
    #Save in a CSV file for now
    today = str(date.today())
    union_df.to_csv(f"Poll_Data-{today}.csv", index=False)

    ## Renaming Columns
    grouped_df = union_df.groupby('DATE', as_index=False)['JOE BIDEN', 'DONALD TRUMP'].mean()
    renamed_df = grouped_df[['DATE', 'JOE BIDEN', 'DONALD TRUMP']]

    ## Plot Settings
    figPres = plt.figure(figsize=(13, 5))
    axPres = figPres.add_subplot()
    plt.ylim(35, 65)

    ## Melt to make it easier to plot
    df_final = pd.melt(renamed_df, id_vars=['DATE'], value_vars=['JOE BIDEN', 'DONALD TRUMP'])
    df_final.rename(columns={'DATE': 'DATE', 'variable': 'CANDIDATE', 'value': 'POLLING PERCENTAGE'}, inplace=True)

    # Draw line plot of size and total_bill with parameters
    sns.lineplot(x="DATE", y="POLLING PERCENTAGE", data=df_final, hue="CANDIDATE",
                 style="CANDIDATE", palette=['b', 'r'], dashes=False,
                 markers=["o", "<"], legend="brief", )

    plt.title("Trump Vs Biden", fontsize=20)  # for title
    plt.xlabel("Poll Date", fontsize=15)  # label for x-axis
    plt.ylabel("Voter Support(%)", fontsize=15, rotation=90)  # label for y-axis

    ## Set the titles of the axes
    axPres.set_ylabel("Voter Support (%)", fontsize=15)
    axPres.yaxis.set_label_coords(-0.07, 0.50)
    axPres.set_xlabel("Poll Date", fontsize=15)

    plt.show()
