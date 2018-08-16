"""
Script for generating

Example run:
>> python create_registration_pairs.py \
    -imgs ../output/synth_dataset/*.jpg \
    -lnds ../output/synth_dataset/*.csv \
    -csv ../output/cover.csv --mode all-all

Copyright (C) 2016-2018 Jiri Borovec <jiri.borovec@fel.cvut.cz>
"""

import os
import sys
import glob
import argparse
import logging

import pandas as pd

sys.path += [os.path.abspath('.'), os.path.abspath('..')]  # Add path to root
import benchmark.utilities.experiments as tl_expt

# list of combination options
OPTIONS_COMBINE = ['first-all', 'all-all']


def arg_parse_params():
    """ parse the input parameters

    :return dict: {str: str}
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-imgs', '--path_pattern_images', type=str,
                        help='path to the input image', required=True)
    parser.add_argument('-lnds', '--path_pattern_landmarks', type=str,
                        help='path to the input landmarks', required=True)
    parser.add_argument('-csv', '--path_csv', type=str, required=True,
                        help='path to coordinate csv file')
    parser.add_argument('--mode', type=str, required=False,
                        help='type of combination of registration pairs',
                        default=OPTIONS_COMBINE[0], choices=OPTIONS_COMBINE)
    args = vars(parser.parse_args())
    logging.info(tl_expt.string_dict(args, 'ARGUMENTS:'))
    assert tl_expt.check_paths(args, ['path_csv']), 'some paths are missing'
    return args


def generate_pairs(df_cover, path_pattern_imgs, path_pattern_lnds, mode):
    """ generate the registration pairs as reference and moving images

    :param DF df_cover: DF
    :param str path_pattern_imgs: path to the images and image name pattern
    :param str path_pattern_lnds: path to the landmarks and its name pattern
    :param str mode: one of OPTIONS_COMBINE
    :return: DF
    """
    list_imgs = sorted(glob.glob(path_pattern_imgs))
    list_lnds = sorted(glob.glob(path_pattern_lnds))
    assert len(list_imgs) == len(list_lnds), \
        'the list of loaded images (%i) and landmarks (%i) ' \
        'is different length' % (len(list_imgs), len(list_lnds))
    assert len(list_imgs) >= 2, 'the minimum is 2 elements'
    logging.info('combining list %i files with "%s"', len(list_imgs), mode)

    if type == 'first-all':
        for i in range(1, len(list_imgs)):
            df_cover = df_cover.append({
                'Reference image': list_imgs[0],
                'Moving image': list_lnds[0],
                'Reference landmarks': list_imgs[i],
                'Moving landmarks': list_lnds[i],
            }, ignore_index=True)
    elif type == 'all-all':
        for i, _ in enumerate(list_imgs):
            for j in range(i + 1, len(list_imgs)):
                df_cover = df_cover.append({
                    'Reference image': list_imgs[i],
                    'Moving image': list_lnds[i],
                    'Reference landmarks': list_imgs[j],
                    'Moving landmarks': list_lnds[j],
                }, ignore_index=True)
    return df_cover


def main(params):
    """ main entry point

    :param dict params: {str: str}
    """
    logging.info('running...')

    # if the cover file exist continue in it, otherwise create new
    if os.path.exists(params['path_csv']):
        logging.info('loading existing csv file')
        df_cover = pd.read_csv(params['path_csv'], index_col=0)
    else:
        logging.info('creating new cover file')
        df_cover = pd.DataFrame()

    df_cover = generate_pairs(df_cover, params['path_pattern_images'],
                              params['path_pattern_landmarks'], params['mode'])

    logging.info('saving csv file with %i records', len(df_cover))
    df_cover.to_csv(params['path_csv'])

    logging.info('DONE')


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    arg_params = arg_parse_params()
    main(arg_params)