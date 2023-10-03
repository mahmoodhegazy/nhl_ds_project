from dataAcquisition import DataAcquisition


if __name__ == '__main__':

    data_aquirer = DataAcquisition()
    seasons = ['20192020', '20202021']
    game_types = ['R', 'P']

    data_aquirer.download_all_play_by_play_data(seasons, game_types)