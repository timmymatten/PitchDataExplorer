from pybaseball import statcast

data = statcast('2024-01-01', '2024-12-31')
data.to_csv('savant_data.csv', index=False)
