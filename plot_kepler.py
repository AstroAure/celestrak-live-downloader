import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import os

mu_earth = 3.986004418e14 # [m^3/s^2]
R_earth = 6.3781e6 # [m]
day = 24*3600 # [s]

sat_ids = os.getenv('SAT_INTDES_IDS', '').split(',')

def plot_elements(axs, sat_id, color='r'):
    # Get data
    csv_path = f"data/{sat_id}.csv"
    df = pd.read_csv(csv_path)
    # Convert data to orbital elements
    epoch = pd.to_datetime(df['EPOCH'])
    ecc = df['ECCENTRICITY']
    inc = df['INCLINATION'] # [deg]
    sma = np.cbrt(mu_earth/(2*np.pi*df['MEAN_MOTION']/day)**2) # [m] (MEAN_MOTION is [rev/day])
    ap = sma * (1+ecc) - R_earth # [m]
    pe = sma * (1-ecc) - R_earth # [m]
    raan = df['RA_OF_ASC_NODE'] # [deg]
    aop = df['ARG_OF_PERICENTER'] # [deg]
    # Plot
    label = df['OBJECT_NAME'].values[-1]
    if label[:6] == 'OBJECT': label = sat_id
    axs[0,0].plot(epoch, ap/1e3, c=color, label=label, marker='D', mec='k')
    axs[0,0].plot(epoch, pe/1e3, c=color, marker='D', mec='k', ls='--')
    axs[0,1].plot(epoch, ecc, c=color, label=label, marker='D', mec='k')
    axs[1,0].plot(epoch, inc, c=color, label=label, marker='D', mec='k')
    axs[1,1].plot(epoch, raan, c=color, label=label, marker='D', mec='k')

if __name__ == '__main__':

    if not sat_ids or sat_ids == ['']:
        raise ValueError("No satellite ids defined in SAT_INTDES_IDS")

    fig, axs = plt.subplots(2,2,figsize=(16,10), gridspec_kw={'hspace':0.4, 'wspace':0.2})

    # colors = plt.get_cmap('hsv')(np.random.random(len(sat_ids)))
    # colors = plt.get_cmap('hsv')(np.linspace(0,0.6,len(sat_ids)))
    colors = ['#006BA4', '#FF800E', '#ABABAB', '#595959', '#5F9ED1', '#C85200', '#898989', '#A2C8EC', '#FFBC79', '#CFCFCF']

    for i, sat_id in enumerate(sat_ids):
        plot_elements(axs, sat_id, color=colors[i%10])

    # Format figure
    axs[0,0].set_title("Altitude [km]")
    axs[0,0].legend()
    axs[0,1].set_title("Eccentricity")
    axs[1,0].set_title("Inclination [deg]")
    axs[1,1].set_title("RAAN [deg]")

    for ax in axs.ravel():
        ax.grid()
        ax.grid(which='minor', alpha=0.3)
        # ax.xaxis.set_major_locator(mdates.HourLocator(interval=12))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%Y %H:%M'))
        ax.set_xticks(ax.get_xticks()[1::2])
        ax.set_xticklabels(ax.get_xticklabels(), rotation=20, ha='right')

    fig.savefig("kepler_elements.png", bbox_inches='tight', pad_inches=0.1, dpi=200)