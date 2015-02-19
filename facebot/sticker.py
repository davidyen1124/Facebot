import json


def get_stickers(fb, stickers):
    '''Get all stickers for the sitcker bundle id.'''
    url = 'https://www.facebook.com/stickers/{}/images'.format(stickers)
    data = {
        "__user": fb.user_id,
        "__a": "1",
        "__dyn": "7n8anEBQ9FoBUSt2u6aAix97xN6yUgByV9GiyFqzQC-C26m6oDAyoSnx2ubhHAyXBBzEy5E",
        "__req": "c",
        "fb_dtsg": fb.dtsg,
        "ttstamp": "26581691011017411284781047297",
        "__rev": "1436610",
    }
    res = fb.session.post(url, data)
    res.raise_for_status()

    # remove for (;;); so we can turn them into dictionaries
    content = json.loads(res.text.replace('for (;;);', ''))

    return content['payload']