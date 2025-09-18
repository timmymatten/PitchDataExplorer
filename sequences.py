import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from savant_data_api import SAVANT_DATA_API

class SEQUENCING_API:

    pitches = None

    sav_api = SAVANT_DATA_API()
        
    def load_data(self):
        # Set up plotting style
        plt.style.use('default')
        sns.set_palette("husl")

        self.sav_api.load_data('savant_data.csv')

        self.pitches = self.sav_api.data.copy()

        # Define pitcher success
        self.pitches['success'] = self.pitches['description'].apply(
            lambda x: 1 if x in ['swinging_strike', 'called_strike', 'foul_tip', 
                    'swinging_strike_blocked', 'foul', 'foul_bunt', 
                    'missed_bunt', 'bunt_foul_tip'] else 0
                    )
        
        # Calculate success rate for each pitch type
        pitch_type_success = self.pitches.groupby('pitch_type').agg(
            total_pitches=('pitch_type', 'count'),
            success_rate=('success', 'mean')
            ).reset_index()
        
        pitch_type_success['percent_total_pitches'] = (
            100 * pitch_type_success['total_pitches'] / pitch_type_success['total_pitches'].sum()
            )
        pitch_type_success['success_rate'] = pitch_type_success['success_rate'].round(4)
        pitch_type_success['percent_total_pitches'] = pitch_type_success['percent_total_pitches'].round(4)
        pitch_type_success = pitch_type_success.sort_values('success_rate', ascending=False)

        # Change NA entries to 'Other'
        pitch_type_success['pitch_type'] = pitch_type_success['pitch_type'].fillna('Other')

        # Categorize pitches into Fastball, Breaking Ball, Off-Speed, Other
        self.pitches['pitch_category'] = self.pitches['pitch_type'].apply(self.categorize_pitch)

    # Create pitch categories
    def categorize_pitch(self, pitch_type):
        if pitch_type in ['FF', 'FA', 'SI', 'FC']:
            return 'Fastball'
        elif pitch_type in ['SL', 'CU', 'KC', 'ST', 'SV', 'SC', 'CS']:
            return 'Breaking Ball'
        elif pitch_type in ['CH', 'FS', 'FO', 'EP', 'KN']:
            return 'Off-Speed'
        elif pitch_type in ['PO', 'Other'] or pd.isna(pitch_type):
            return 'Other'
        else:
            return 'Other'
        
    def get_clean_pitches(self):
        exclude_desc = ['foul_bunt', 'missed_bunt', 'bunt_foul_tip', 'pitchout']

        return self.pitches[
            (~self.pitches['description'].isin(exclude_desc)) & 
            (self.pitches['pitch_category'] != 'Other') &
            (self.pitches['pitch_category'].notna())
        ].copy()

    def get_sequences(self):
        # Take out anomaly events
        
        pitches_clean = self.get_clean_pitches()

        # Arrange the pitches into at bats
        pitch_seq = pitches_clean.sort_values(
            ['game_date', 'game_pk', 'at_bat_number', 'pitch_number']
        )[['game_date', 'game_pk', 'at_bat_number', 'inning_topbot', 'inning', 
        'batter', 'pitch_number', 'balls', 'strikes', 'pitch_type', 
        'pitch_category', 'success', 'plate_x', 'plate_z', 'outs_when_up']].copy()

        # Find pitch sequences - create three pitch sequences
        three_pitch_seq = pitch_seq.copy()
        three_pitch_seq['first_pitch'] = three_pitch_seq.groupby(['game_pk', 'at_bat_number'])['pitch_category'].shift(2)
        three_pitch_seq['second_pitch'] = three_pitch_seq.groupby(['game_pk', 'at_bat_number'])['pitch_category'].shift(1)
        three_pitch_seq['third_pitch'] = three_pitch_seq['pitch_category']

        # Filter out rows with incomplete sequences
        three_pitch_seq = three_pitch_seq[three_pitch_seq['first_pitch'].notna()].copy()

        # Create state counts
        three_pitch_seq['state'] = three_pitch_seq['first_pitch'] + '+' + three_pitch_seq['second_pitch']

        return three_pitch_seq

    def get_transition_matrix(self):
        three_pitch_seq = self.get_sequences()
        state_counts = three_pitch_seq.groupby(['state', 'third_pitch']).size().reset_index(name='n')

        # Create Transition Matrix
        transition_matrix = state_counts.pivot(index='state', columns='third_pitch', values='n').fillna(0)
        transition_matrix_prop = transition_matrix.div(transition_matrix.sum(axis=1), axis=0)

        return transition_matrix

    def get_expectancy_matrix(self):

        # Create Expectancy Matrix
        three_pitch_seq_suc = self.get_sequences()
        
        # Calculate expectancy matrix
        expectancy_data = three_pitch_seq_suc.groupby(
            ['first_pitch', 'second_pitch', 'third_pitch']
        )['success'].mean().reset_index(name='success_rate')

        expectancy_data['state'] = expectancy_data['first_pitch'] + '+' + expectancy_data['second_pitch']
        expectancy_matrix = expectancy_data.pivot(
            index='state', columns='third_pitch', values='success_rate'
        ).fillna(0)
        
        return expectancy_matrix

    def get_successes(self):
        # Calculate baseline success by category
    
        category_success = self.get_clean_pitches().groupby('pitch_category').agg(
            total_pitches=('pitch_category', 'count'),
            baseline_success=('success', 'mean')
        ).reset_index()
        category_success = category_success.sort_values('baseline_success', ascending=False)

        return category_success

    def get_heatmaps(self, heat_type, width, height):
        
        # Prepare data for heat maps
        expectancy_matrix = self.get_expectancy_matrix()
        long_matrix = expectancy_matrix.reset_index().melt(
            id_vars=['state'], var_name='third_pitch', value_name='success_rate'
        )

        # Join with baseline success
        category_success = self.get_successes()
        baseline_dict = category_success.set_index('pitch_category')['baseline_success'].to_dict()
        long_matrix['baseline_success'] = long_matrix['third_pitch'].map(baseline_dict)
        
        # Handle division by zero and create success lift
        long_matrix['success_lift'] = np.where(
            long_matrix['baseline_success'] > 0,
            long_matrix['success_rate'] / long_matrix['baseline_success'],
            1.0
        )


        plt.figure(figsize=(width, height))

        if heat_type == 'Raw Success Rate':
            # Raw Success Rate Heat Map
            pivot_success = long_matrix.pivot(index='state', columns='third_pitch', values='success_rate')
            sns.heatmap(pivot_success, annot=True, fmt='.3f', cmap='RdBu_r', center=0.45,
                        cbar_kws={'label': 'Success Probability'})
            
            plt.grid(False)
            plt.title('Effectiveness of 3-Pitch Sequences')
            plt.xlabel('Third Pitch (Category)')
            plt.ylabel('First + Second Pitch (Sequence)')

            plt.tight_layout()
            return plt.gcf()
        else:
            # Success Lift Heat Map
            pivot_lift = long_matrix.pivot(index='state', columns='third_pitch', values='success_lift')
            sns.heatmap(pivot_lift, annot=True, fmt='.3f', cmap='RdBu_r', center=1, 
                        cbar_kws={'label': 'Success Lift'})

            plt.grid(False)
            plt.title('Relative Effectiveness of 3-Pitch Sequences')
            plt.xlabel('Third Pitch (Category)')
            plt.ylabel('First + Second Pitch (Sequence)')

            plt.tight_layout()
            return plt.gcf()