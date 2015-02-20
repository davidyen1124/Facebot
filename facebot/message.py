# -*- encoding: utf-8 -*-
import logging
try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode
import re
import time

import requests

log = logging.getLogger('facebook')
log.setLevel(logging.WARN)

MESSAGE_URL = 'https://www.facebook.com/ajax/mercury/send_messages.php'
UPLOAD_URL = 'https://upload.facebook.com/ajax/mercury/upload.php?'
TYP_URL = 'https://www.facebook.com/ajax/messaging/typ.php'
READ_URL = 'https://www.facebook.com/ajax/mercury/change_read_status.php'

# define like sticker id
LIKE_STICKER = {
    'l': '369239383222810',
    'm': '369239343222814',
    's': '369239263222822'
}


def send_group(fb, thread, body, pic=None, sticker=None, like=None):
    data = {
        "message_batch[0][action_type]": "ma-type:user-generated-message",
        "message_batch[0][author]": "fbid:{}".format(fb.user_id),
        "message_batch[0][source]": "source:chat:web",
        "message_batch[0][body]": body,
        "message_batch[0][signatureID]": "3c132b09",
        "message_batch[0][ui_push_phase]": "V3",
        "message_batch[0][status]": "0",
        "message_batch[0][thread_fbid]": thread,
        "client": "mercury",
        "__user": fb.user_id,
        "__a": "1",
        "__dyn": "7n8anEBQ9FoBUSt2u6aAix97xN6yUgByV9GiyFqzQC-C26m6oDAyoSnx2ubhHAyXBBzEy5E",
        "__req": "c",
        "fb_dtsg": fb.dtsg,
        "ttstamp": "26581691011017411284781047297",
        "__rev": "1436610",
    }

    if pic:
        # upload the picture and get picture form data
        pic_data = upload_picture(fb, pic)
        if pic_data:
            # merge together to send message with picture
            data.update(pic_data)

    # add sticker if sticker is available
    if any([sticker, like]):
        # if like is not None, find the corresponding sticker id
        if like:
            try:
                sticker = LIKE_STICKER[like.lower()]
            except KeyError:
                # if user doesn't enter l or m or s, then use the large one
                sticker = LIKE_STICKER['l']

        data["message_batch[0][sticker_id]"] = sticker

    fb.session.post(MESSAGE_URL, data)


def send_person(fb, person, body, pic=None, sticker=None, like=None):
    data = {
        "message_batch[0][action_type]": "ma-type:user-generated-message",
        "message_batch[0][author]": "fbid:{}".format(fb.user_id),
        "message_batch[0][source]": "source:chat:web",
        "message_batch[0][body]": body,
        "message_batch[0][signatureID]": "3c132b09",
        "message_batch[0][ui_push_phase]": "V3",
        "message_batch[0][status]": "0",
        "message_batch[0][specific_to_list][0]": "fbid:{}".format(person),
        "message_batch[0][specific_to_list][1]": "fbid:{}".format(fb.user_id),
        "client": "mercury",
        "__user": fb.user_id,
        "__a": "1",
        "__dyn": "7n8anEBQ9FoBUSt2u6aAix97xN6yUgByV9GiyFqzQC-C26m6oDAyoSnx2ubhHAyXBBzEy5E",
        "__req": "c",
        "fb_dtsg": fb.dtsg,
        "ttstamp": "26581691011017411284781047297",
        "__rev": "1436610",
    }

    if pic:
        # upload the picture and get picture form data
        pic_data = upload_picture(fb, pic)
        if pic_data:
            # merge together to send message with picture
            data.update(pic_data)

    # add sticker if sticker is available
    if any([sticker, like]):
        # if like is not None, find the corresponding sticker id
        if like:
            try:
                sticker = LIKE_STICKER[like.lower()]
            except KeyError:
                # if user doesn't enter l or m or s, then use the large one
                sticker = LIKE_STICKER['l']

        data["message_batch[0][sticker_id]"] = sticker

    fb.session.post(MESSAGE_URL, data)


def upload_picture(fb, pic):
    params = {
        "__user": fb.user_id,
        "__a": "1",
        "__dyn": "7n8anEBQ9FoBUSt2u6aAix97xN6yUgByV9GiyFqzQC-C26m6oDAyoSnx2ubhHAyXBBzEy5E",
        "__req": "c",
        "fb_dtsg": fb.dtsg,
        "ttstamp": "26581691011017411284781047297",
        "__rev": "1436610",
        'ft[tn]': '+M',
    }

    # upload the image to facebook server, filename should be unique
    res = fb.session.post(UPLOAD_URL + urlencode(params), files={
        'images_only': 'true',
        'upload_1024': (str(time.time()), requests.get(pic).content, 'image/jpeg')
    })

    # check status code
    if res.status_code != 200:
        return

    # check image_id is valid
    m = re.search(r'"image_id":(\d+),', res.text)
    if not m:
        return

    image_id = m.group(1)
    return {
        "message_batch[0][has_attachment]": "true",
        "message_batch[0][preview_attachments][0][upload_id]": "upload_1024",
        "message_batch[0][preview_attachments][0][attach_type]": "photo",
        "message_batch[0][preview_attachments][0][preview_uploading]": "true",
        "message_batch[0][preview_attachments][0][preview_width]": "540",
        "message_batch[0][preview_attachments][0][preview_height]": "720",
        "message_batch[0][image_ids][0]": image_id,
    }


def group_typing(fb, thread):
    data = {
        "typ": "1",
        "to": "",
        "source": "web-messenger",
        "thread": thread,
        "__user": fb.user_id,
        "__a": "1",
        "__dyn": "7n8anEBQ9FoBUSt2u6aAix97xN6yUgByV9GiyFqzQC-C26m6oDAyoSnx2ubhHAyXBBzEy5E",
        "__req": "c",
        "fb_dtsg": fb.dtsg,
        "ttstamp": "26581691011017411284781047297",
        "__rev": "1436610",
    }

    fb.session.post(TYP_URL, data)


def person_typing(fb, thread):
    data = {
        "typ": "1",
        "to": thread,
        "source": "web-messenger",
        "thread": thread,
        "__user": fb.user_id,
        "__a": "1",
        "__dyn": "7n8anEBQ9FoBUSt2u6aAix97xN6yUgByV9GiyFqzQC-C26m6oDAyoSnx2ubhHAyXBBzEy5E",
        "__req": "c",
        "fb_dtsg": fb.dtsg,
        "ttstamp": "26581691011017411284781047297",
        "__rev": "1436610",
    }

    fb.session.post(TYP_URL, data)


def read(fb, thread):
    data = {
        "ids[{}]".format(thread): "true",
        "__user": fb.user_id,
        "__a": "1",
        "__dyn": "7n8anEBQ9FoBUSt2u6aAix97xN6yUgByV9GiyFqzQC-C26m6oDAyoSnx2ubhHAyXBBzEy5E",
        "__req": "c",
        "fb_dtsg": fb.dtsg,
        "ttstamp": "26581691011017411284781047297",
        "__rev": "1436610",
    }

    fb.session.post(READ_URL, data)
