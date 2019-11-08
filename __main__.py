# FOAR705 2019 Proof of Concept
# Matthew Clark | 43695841
#
#
# Preamble #
import json
import time
from time import sleep
import timeit
import numpy as np
import oauth2 as oauth



start = timeit.default_timer()
# Authentication #
# Private consumer discogs API keys
consumer_key = 'insertconsumerkeyhere'
consumer_secret = 'insertconsumersecrethere'

# Unique user agent
user_agent = 'insertuniqueuseragenthere'

# Oauth Consumer and Client objects
consumer = oauth.Consumer(consumer_key, consumer_secret)

# Verification token from Discogs
oauth_verifier = 'oathverificationcode'

# Handshaking with Discogs' server
token = oauth.Token('oathtokenkey', 'oauthtokensecret')
token.set_verifier(oauth_verifier)
token = oauth.Token(key='oathtokenkey',
                    secret='oathtokensecret')
client = oauth.Client(consumer, token)


# Retrieving search query from discogs
def getContent(requesturl):
    resp, content = (client.request(
        requesturl, headers={'User-Agent': user_agent}))
    return resp, content


# Main Program
def call_catching():
    global y
    print 'Program started'
    # Create array which will be used to export my data; add headings for each column
    data_set = np.empty((1, 11), dtype=np.dtype('U50'))
    data_set[0, 0] = 'ID'
    data_set[0, 1] = 'Artist'
    data_set[0, 2] = 'Release_Title'
    data_set[0, 3] = 'Style'
    data_set[0, 4] = 'Year'
    data_set[0, 5] = 'Country'
    data_set[0, 6] = 'Label'
    data_set[0, 7] = 'Format'
    data_set[0, 8] = 'Have'
    data_set[0, 9] = 'Want'
    data_set[0, 10] = 'Mean'

    for year in range(2019, 1988, -1):

        # Local variables
        i = 0
        style = 'techno'
        url = 'https://api.discogs.com/database/search?style=' + style + '&year=' + str(
            year) + '&per_page=100&type=release'

        # Start the timer to keep track of request limit
        start_timer = time.time()

        # Define variables from data pulled from API
        retrieve_data = getContent(url)
        yearly_releases = json.loads(retrieve_data[1])
        rate_limiter = retrieve_data[0]['x-discogs-ratelimit-remaining']
        next_page = str(yearly_releases['pagination']['urls']['next'])

        # Define range based off multiples of 100
        total_elements = yearly_releases['pagination']['items']
        if total_elements > 10000:
            max_range = 10000
        else:
            max_range = (total_elements / 100) * 100

        # New array to transform retrieved data in
        data_sort = np.empty((max_range, 11), dtype=np.dtype('U50'))

        print 'Currently processing Year', year

        for j in range(0, max_range, 100):
            for release in yearly_releases['results']:
                # Data Calculations
                title_release = release.get('title', 'unknown')
                title_release_split = title_release.split('-', 2)
                title = title_release_split[0]
                delimited_title = title.replace(u',', u';')
                release_name = title_release_split[1]
                delimited_release = release_name.replace(u',', u';')
                community_input = release.get('community', 'unknown')
                have = community_input['have']
                want = community_input['want']
                have_want_mean = (have + want) / 2

                # Fill in array
                data_sort[i + j, 0] = release.get('id')
                data_sort[i + j, 1] = delimited_title
                data_sort[i + j, 2] = delimited_release
                data_sort[i + j, 3] = '; '.join(release.get('style'))
                data_sort[i + j, 4] = release.get('year')
                data_sort[i + j, 5] = (release.get('country')).replace(u',', u';')
                data_sort[i + j, 6] = ('; '.join(release.get('label'))).replace(u',', u';')
                data_sort[i + j, 7] = ('; '.join(release.get('format'))).replace(u',', u';')
                data_sort[i + j, 8] = have
                data_sort[i + j, 9] = want
                data_sort[i + j, 10] = format(have_want_mean, "05")
                i = i + 1
            print 'Year:', year, ' | Number of entries processed: ', j, ' | Number of requests left: ' + rate_limiter

            # Safety net for request rate limit
            end_timer = time.time()
            elapsed_time = end_timer - start_timer
            if elapsed_time < 1:
                sleep(1.1 - elapsed_time)
            if rate_limiter == 1:
                print 'Request limit reached. Resuming in 60s...'
                sleep(61)
            start_timer = time.time()

            # Safety Net 1
            if j < max_range - 100:
                retrieve_data = getContent(next_page)
                yearly_releases = json.loads(retrieve_data[1])
                # Safety Net 2
                if 'next' in yearly_releases['pagination']['urls']:
                    next_page = str(yearly_releases['pagination']['urls']['next'])
                rate_limiter = retrieve_data[0]['x-discogs-ratelimit-remaining']
                i = 0

        print 'Transforming data:'
        # Sort by Style
        sorted_by_style = data_sort[data_sort[:, 3].argsort()[::-1]]

        # Find range of elements which only have the style 'Techno'
        z = 0
        while sorted_by_style[z, 3] != 'Techno':
            z += 1
            y = z
            while sorted_by_style[y, 3] == 'Techno':
                y += 1

        # 1: Remove any rows which contain more than the style 'Techno' if applicable
        # 2: Sort the new array by the mean column
        # 3: Remove duplicates from the sorted array using np.unique
        # 4: Extract the first 100 rows by removing all elements below
        # 5: Concatenate new array of 100 entries to data_set
        # 6: Repeat process with the year before
        print '     Removing cross-style entries...'
        if z > 0:
            techno_only = sorted_by_style[z:y]
            techno_only = unique(techno_only)
            techno_only_sorted = techno_only[techno_only[:, 10].argsort()[::-1]]
        else:
            sorted_by_style = unique(sorted_by_style)
            techno_only_sorted = sorted_by_style[sorted_by_style[:, 10].argsort()[::-1]]
        print '     Concatenating data...'
        top_100_techno = techno_only_sorted[:100]
        data_set = np.concatenate((data_set, top_100_techno))
        print '    ', year, 'finished'

    print '     Editing Nulls...'
    data_set = edit_nulls(data_set)
    return data_set


# Method which removes duplicated entries
def unique(arr):
    print '     Removing duplicates...'
    arr = arr[arr[:, 0].argsort()[::-1]]
    i = 0
    while i < arr.__len__()-1:
        if arr[i, 0] == arr[i + 1, 0]:
            arr = np.delete(arr, i + 1, 0)
        else:
            i = i + 1
    return arr


# Change 'Unknown' null values to 'Blank
def edit_nulls(arr):
    for i in range(0, 10, 1):
        for j in range(0, 99, 1):
            if arr[j, i] == 'Unknown':
                arr[j, i] = 'Blank'
    return arr


def startProgram():
    data_set = call_catching()
    print'Exporting to file'
    np.savetxt('43695841_dataSet.csv', data_set, fmt='%s', delimiter=',', encoding='utf=8')
    print 'Exported Successfully'
    stop = timeit.default_timer()
    print 'Execution Time: ', ((stop - start)/60), 'minutes'


startProgram()
