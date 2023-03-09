import multiprocessing
import os
import pickle
import random
from multiprocessing import freeze_support

from gensim.parsing import preprocess_string
from textattack.augmentation import DeletionAugmenter
from textattack.augmentation.recipes import SwapAugmenter

labels = ['HADOOP','HDFS', 'OFBIZ', 'MAPREDUCE','HHH', 'CASSANDRA']

prjs= [
    {
        "project": 'ZooKeeper',
        "project_path_name": 'zookeeper'
    },
    {
        "project": 'HBase',
        "project_path_name": 'hbase'
    },
    {
        "project": 'Hive',
        "project_path_name": 'hive'
    },
    {
        "project": 'Hibernate ORM',
        "project_path_name": 'hibernate-orm'
    },
    {
        "project": 'Cassandra',
        "project_path_name": 'cassandra'
    },
    {
        "project": 'Harmony',
        "project_path_name": 'harmony'
    },
    {
        "project": 'Wicket',
        "project_path_name": 'wicket'
    },
]

augmenter = DeletionAugmenter(pct_words_to_swap=0.1,transformations_per_example=1)
augmenter_2 = SwapAugmenter(pct_words_to_swap=0.1,transformations_per_example=1)


def augment(key, removed, comments):
    path = 'h:\\reports\\defect_r1\\adv\\' + key + '.txt'
    if os.access(path, os.F_OK):
        return
    print('assessing '+path)

    comments_arr = comments.split(' ')
    removed_arr = removed.split(' ')
    base = 0
    res = key+':'+' '.join(preprocess_string(removed)) + ' @C@ ' + ' '.join(preprocess_string(comments))+'\n'
    txt_adv = [[],[],[],[]]
    while base < len(removed_arr):
        current_removed = removed_arr[base:base+50]

        base+=50

        print('processing '+key)
        for idx, txt in enumerate(list(map(preprocess_string, augmenter.augment(' '.join(current_removed))))):
            txt_adv[idx].extend(txt)
        for idx, txt in enumerate(list(map(preprocess_string, augmenter_2.augment(' '.join(current_removed))))):
            txt_adv[idx].extend(txt)
    for i in range(0,2):
        txt_adv[i].append(' @C@ ')

    base = 0
    while base < len(comments_arr):
        current_removed = comments_arr[base:base+50]

        base+=50

        print('processing '+key)
        for idx, txt in enumerate(list(map(preprocess_string, augmenter.augment(' '.join(current_removed))))):
            txt_adv[idx].extend(txt)

    for i in range(0, 2):
        new_key = key + '_adv_' + str(i)
        try:
            res += new_key+':'+' '.join(txt_adv[i]) +'\n'
        except:
            res += new_key + ':' + ' '.join(txt_adv[i]) + '\n'
    res= res[:-1]
    try:
        with open(path, 'w') as f1:
            print(res)
            f1.write(res)
    except:
        1

import psutil

# to kill stucked process
def kills(pid):
    '''Kills all process'''
    parent = psutil.Process(pid)
    for child in parent.children(recursive=True):
        child.kill()
    parent.kill()

if __name__ == '__main__':
    freeze_support()
    base = 'h:\\reports\\defect_r1\\adv\\' # use your own directory
    with open(base+'input.pk', 'rb') as f2:
        input = pickle.load(f2)
    input_real = []
    for i in input:
        k, a, b = i
        kk = k.split('-')[0]
        path = base + k + '.txt'
        if os.access(path, os.F_OK):
            continue
        input_real.append(i)
    random.shuffle(input_real)
    print(len(input_real))
    pool = multiprocessing.Pool(processes=20)
    pool.starmap(augment, input_real)
