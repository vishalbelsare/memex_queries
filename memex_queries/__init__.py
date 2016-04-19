import datetime as dt
from HelperFuncs import post_dates_for_general_cdr_image_id
from HelperFuncs import cdr_ad_ids_for_general_cdr_image_id
from HelperFuncs import dd_df_from_sqlite_tables
from HelperFuncs import dd_id_from_cdr_id


def query_one(cdr_image_id, es=None):
    """
    For a given image cdr_image_id, return the first date (in the CDR) that it appeared)
    Currently: Get the image from the CDR
    Hit Svebor's table to get the image hash.
    If that doesn't work, hit the image binary and get the SHA1 yourself.
    Hit Svebor's table for the list of related ads. If that doesn't work,
    give up.
    Hit Svebor's table for a list of timestamps.
    If that doesn't work, hit elastic
    :param str cdr_image_id: The CDR ID of the image to retrieve
    :param elasticsearch.Elasticsearch es: the elasticsearch index to search
    :return datetime.datetime:
    """
    return min(post_dates_for_general_cdr_image_id(cdr_image_id, es))


def query_two(cdr_image_id):
    """
    For a given cdr_image_id, what phone number (or numbers) posted ads using image_id
    on the first date (in the CDR) that it appeared?
    :param str cdr_image_id: The CDR ID of the image to retrieve
    :return set:
    """
    dd_ad_ids = [dd_id_from_cdr_id(x) for x in cdr_ad_ids_for_general_cdr_image_id(cdr_image_id)]
    df = dd_df_from_sqlite_tables(dd_ad_ids, ['dd_id_to_phone', 'dd_id_to_post_date'])
    first_date = df.post_date.min()

    return set(df.ix[(df.post_date == first_date), 'phone'].values)


def query_three(cdr_image_id, post_date):
    """
    For a given cdr_image_id at post_date
    WHAT phone numbers posted ads with cdr_image_id at an earlier date?
    :param str cdr_image_id: The CDR ID of the image to retrieve
    :param str|datetime.datetime post_date: Date against which to check
    :return set:
    """
    dd_ad_ids = [dd_id_from_cdr_id(x) for x in cdr_ad_ids_for_general_cdr_image_id(cdr_image_id)]
    df = dd_df_from_sqlite_tables(dd_ad_ids, ['dd_id_to_phone', 'dd_id_to_post_date'])

    if isinstance(post_date, str):
        post_date = dt.datetime(str)

    return set(df.ix[df.post_date < post_date, 'phone'])


def query_four(cdr_image_id, post_date):
    """
    For a given cdr_image_id ~~posted by phone_number~~ at post_date,
    HOW MANY phone numbers posted ads with I at an earlier date?
    :param str cdr_image_id: The CDR ID of the image to retrieve
    :param str|datetime.datetime post_date: Date against which to check
    :return int:
    """
    return len(query_three(cdr_image_id, post_date))


def query_five(cdr_image_id):
    """
    For a given cdr_image_id, what phone numbers posted ads using it?
    :param str cdr_image_id: The CDR ID of the image to retrieve
    :return set:
    """
    dd_ad_ids = [dd_id_from_cdr_id(x) for x in cdr_ad_ids_for_general_cdr_image_id(cdr_image_id)]
    return set(dd_df_from_sqlite_tables(dd_ad_ids, ['dd_id_to_phone']).phone)


def query_six(cdr_image_id):
    """
    For a given cdr_image_id, how many phone numbers posted ads using it?
    :param str cdr_image_id: The CDR ID of the image to retrieve
    :return int:
    """
    return len(query_five(cdr_image_id))


def query_seven(cdr_image_id, phone_number, post_date):
    """
    For a given cdr_image_id posted by phone_number on post_date
    what phone numbers OTHER THAN PHONE_NUMBER posted ads with image_id at an earlier date?
    :param str cdr_image_id: The CDR ID of the image to retrieve
    :param str phone_number:
    :param str|datetime.datetime post_date: Date against which to check
    :return:
    """
    dd_ad_ids = [dd_id_from_cdr_id(x) for x in cdr_ad_ids_for_general_cdr_image_id(cdr_image_id)]
    df = dd_df_from_sqlite_tables(dd_ad_ids, ['dd_id_to_phone', 'dd_id_to_post_date'])

    if isinstance(post_date, str):
        post_date = dt.datetime(post_date)

    return set(df.ix[(df.phone != phone_number) & df.post_date < post_date, 'phone'].values)


def query_eight(image_id, phone_number, post_date):
    """
    For a given image_id posted by phone_number at post_date,
    HOW MANY phone numbers other than P posted ads with I at an earlier date?
    :param str image_id: The CDR ID of the image to retrieve
    :param str phone_number:
    :param str|datetime.datetime post_date: Date against which to check
    :return int:
    """
    return len(query_seven(image_id, phone_number, post_date))


def query_nine(cdr_ad_id, phone_number=None):
    """
    For a given cdr_ad_id posted by phone_number
    what fraction of the images were first used in ads posted by by phone numbers other than P?
    :param str cdr_ad_id: The CDR ID of an ad
    :param str phone_number:
    :return:
    """
    dd_ad_id = dd_id_from_cdr_id(cdr_ad_id)


def query_ten(cdr_ad_id):
    """
    For all of the images affiliated with a given ad_id,
    if you find which phone number originated each ad, how many total sources does the ad have?
    :param str cdr_ad_id: The CDR ID of an ad
    :return:
    """


def query_eleven(image_id, epochtime=None, es=None):
    """
    For a given image posted at a certain time, how long has it been since the image was last posted?
    :param str image_id: The CDR ID of the image to retrieve
    :param int epochtime: if None, assume we're talking about the gap between the most and second-most recent instance
    if an int, find the first timestamp BEFORE the one provided.
    :param elasticsearch.Elasticsearch es:
    :return int: epochtime since the last posting
    """
    ad_timestamps = sorted(post_dates_for_general_cdr_image_id(image_id, es))

    if epochtime is None:
        # If there's been no postings, the gap is infinite
        if len(ad_timestamps) < 1:
            return None

        # If there's been one posting, the gap is 0
        if len(ad_timestamps) < 2:
            return 0

        return ad_timestamps[-1] - ad_timestamps[-2]

    for ts in ad_timestamps[::-1]:
        if ts < epochtime:
            return epochtime - ts

    return 0


def query_twelve(cdr_image_id):
    """
    For a given image_id, what is its radius of gyration?
    :param str cdr_image_id: The CDR ID of the image to retrieve
    :return:
    """


def query_thirteen():
    """
    Estimate \gamma for arrival rate under Poisson or some other similar thing
    :return:
    """


def query_fourteen(cdr_ad_id):
    """
    For a given cdr_ad_id posted at time T,
    what fraction of the images have not been used in prior ads?
    :param str cdr_ad_id: The CDR ID of an ad
    :return:
    """


def query_fifteen(cdr_ad_id):
    """
    For a given cdr_ad_id posted at time T, what is the mean number of times images in the ad have appeared before?
    :param str cdr_ad_id: The CDR ID of an ad
    :return:
    """


def query_sixteen(cdr_ad_id):
    """
    For a given cdr_ad_id, what is the mean amount time since ads in the photos first appeared?
    :param str cdr_ad_id: The CDR ID of an ad
    :return:
    """


def query_seventeen(cdr_image_id):
    """
    For a given image_id, what is the median price in all ads using this photo?
    :param str cdr_image_id: The CDR ID of the image to retrieve
    :return:
    """


def query_eighteen(cdr_image_id):
    """
    For a given image_id, what proportion of ads including that image offer outcall services?
    :param str cdr_image_id: The CDR ID of the image to retrieve
    :return:
    """


def query_nineteen(cdr_image_id):
    """
    For a given image_id,
    what is the Lat-long of the centroid defined by the locations provided for the advertisements
    in which I has been used?
    :param str cdr_image_id: The CDR ID of the image to retrieve
    :return:
    """


def query_twenty(cdr_image_id):
    """
    For a given image_id used in an ad at time T,
    what is the largest Photo Gap (query_eleven) that has been seen for any use of the I in prior ads?
    :param str cdr_image_id: The CDR ID of the image to retrieve
    :return:
    """


def query_twenty_one():
    """
    query_seven and query_seventeen are general attempts at finding time period clusters for images.
    A specific time-based cluster of images would be useful.
    :return:
    """


def query_twenty_two(cdr_ad_id):
    """
    For a given ad_id
    with a set of images (I),
    what is the first date on which an ad using exactly (I) appeared?
    :param str cdr_ad_id: The CDR ID of an ad
    :return:
    """


def query_twenty_three(cdr_ad_id):
    """
    For a given ad_id with a set of images (I),
    what is the first date on which an ad using (I) or a superset of (I) appeared?
    :param str cdr_ad_id: The CDR ID of an ad
    :return:
    """


def query_twenty_four(cdr_ad_id):
    """
    For a given ad_id with a set of images (I) posted at time T,
    how many prior ads have used exactly (I)?
    :param str cdr_ad_id: The CDR ID of an ad
    :return:
    """


def query_twenty_five(cdr_ad_id):
    """
    For a given ad_id with a set of images (I) posted at time T,
    how many prior ads have used (I) or a superset of (I)?
    :param str cdr_ad_id: The CDR ID of an ad
    :return:
    """