"""

API for extracting data from savant_data.csv file

"""

import pandas as pd

class SAVANT_DATA_API:

    data = None

    def load_data(self, filename):
        """
        Load the savant data into the object. Clean the data into usable format.
        filename - the name of the csv file containing the pitcher data
        """
        # load the data
        self.data = pd.read_csv(filename)

    def get_pitchers(self):
        """
        Returns a list of pitchers in the data.
        """
        pitchers = self.data['player_name'].unique()
        pitchers.sort()
        return list(pitchers)

    def get_pitcher_data(self, pitcher):
        """
        Returns a dataframe containing all the data for a given pitcher.
        pitcher - value in 'player_name' column of savant_data.csv ('Last_First')
        """
        return self.data[self.data['player_name'] == pitcher]

    def get_pitch_types(self, pitcher):
        """
        Returns a list of pitch types for a given pitcher.
        """

        return list(self.data[self.data['player_name'] == pitcher]['pitch_type'].unique())

    def get_stat_sum(self, stat, player):
        """
        Returns the sum of the given stat for a given player.
        stat - column name in savant_data.csv
        player - value in 'player_name' column of savant_data.csv ('Last_First')
        """
        sum = self.data[self.data['player_name'] == player][stat].sum()
        return sum

    def get_stat_mean(self, stat, player):
        """
        Returns the sum of the given stat for a given player.
        stat - column name in savant_data.csv
        player - value in 'player_name' column of savant_data.csv ('Last_First')
        """
        mean = self.data[self.data['player_name'] == player][stat].mean()
        return mean

def main():
    """
    test functions
    """
    savant = SAVANT_DATA_API()
    savant.load_data('savant_data.csv')
    print(savant.data)
    print(savant.get_stat_sum('release_speed', 'Cole, Gerrit'))

if __name__ == '__main__':
    main()