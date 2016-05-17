
import numpy as np
import pandas as pd
import random
random.seed(0)

train = pd.read_csv('train.csv',
                    dtype={'user_id': np.int32,
                           'user_location_country': np.int32,
                           'is_mobile': bool,
                           'srch_destination_id': np.int32,
                           'srch_adults_cnt': np.int32,
                           'srch_children_cnt': np.int32,
                           'srch_rm_cnt': np.int32,
                           'hotel_country' : np.int32,
                           'is_booking':bool,
                           'hotel_cluster':np.int32},
                    usecols=['user_id',
                             'user_location_country',
                             'is_mobile',
                             'srch_destination_id',
                             'srch_adults_cnt',
                             'srch_children_cnt',
                             'srch_rm_cnt',
                             'hotel_country',
                             'is_booking',
                             'hotel_cluster']).sample(frac = 0.10)



Y = train['hotel_cluster']

X = train.ix[:,0:9]


from sklearn.cross_validation import train_test_split
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size = 0.20, random_state = 0)


def predictByID(id, df):
    ''' 
    This function return 5 hotel_cluster values for each input id
    If an id has 5 or more is_booking counts, then return the top 5 hotel_cluster
    found in the train data.
    If an id has less than 5 is_booking counts,
    return the is_booking clusters and several top nth not booked cluster.
    '''
    counts_is_booking = df.ix[ (df['user_id'] == id) & (df['is_booking'] == 1)].shape[0] 
    # find how many is_booking counts of an id has
    
    if counts_is_booking >=5:
        top5 = situationOne(id, df)
    elif counts_is_booking < 5:
        top5 = situationTwo(id, df)
    else:
        print ('SOMETHING IS WRONG WITH THE CODE!!!')
        top5 = -9999
    return top5

def situationOne(id, df):
#     use this function if counts_is_booking >= 5
    tempDf = df.ix[ (df['user_id'] == id)]
    tempDf2 = tempDf.ix[df['is_booking'] == 1]
    top5 = pd.DataFrame(tempDf2['hotel_cluster'].value_counts().nlargest(5).index)

    return top5


def situationTwo(id, df):
    # use this function if counts_is_booking < 5 and counts_all > 5
    tempDf = df.ix[ (df['user_id'] == id)]
    tempDf2 = tempDf.ix[df['is_booking'] == 1]
    tempDf3 = tempDf.ix[df['is_booking'] == 0]
    top = pd.DataFrame(tempDf2['hotel_cluster'].value_counts().nlargest(5).index)
    number_of_clusters = tempDf2.shape[0]
    still_need = 5 - number_of_clusters
    top_2nd_part = pd.DataFrame(tempDf3['hotel_cluster'].value_counts().nlargest(still_need).index)
    top5 = top.append(top_2nd_part)

    return top5

tr = pd.concat([X_train, Y_train], axis = 1)

train.shape

a = 0
prediction = pd.DataFrame()
for idx, row in X_test['user_id'].iteritems():

    if a < 100000000000:
        prd = pd.DataFrame(predictByID(row, tr))
        prd.columns = ['clusters']
        d = {'ID': pd.Series(row),
             'hote_cluster': " ".join(list(prd['clusters'].astype(str)))}
        tempDF = pd.DataFrame(d)
        prediction = prediction.append(tempDF)
        a += 1
        if a % 1000 == 0:
            print ('Working hard...')
            print ('ID is %d' % row)
