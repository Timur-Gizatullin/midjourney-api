from fastapi import APIRouter, UploadFile

from lib.api import discord
from lib.api.discord import TriggerType
from util._queue import taskqueue
from .handler import prompt_handler, unique_id
from .schema import (
    TriggerExpandIn,
    TriggerImagineIn,
    TriggerUVIn,
    TriggerResetIn,
    QueueReleaseIn,
    TriggerResponse,
    TriggerZoomOutIn,
    UploadResponse,
    TriggerDescribeIn,
    SendMessageResponse,
    SendMessageIn,
)

router = APIRouter()


async def imagine(body: TriggerImagineIn):
    trigger_id, prompt = prompt_handler(body.prompt, body.picurl)
    trigger_type = TriggerType.generate.value

    taskqueue.put(trigger_id, discord.generate, prompt)
    return {"trigger_id": trigger_id, "trigger_type": trigger_type}


async def upscale(body: TriggerUVIn):
    trigger_id = body.trigger_id
    trigger_type = TriggerType.upscale.value

    taskqueue.put(trigger_id, discord.upscale, **body.dict())
    return {"trigger_id": trigger_id, "trigger_type": trigger_type}


async def variation(body: TriggerUVIn):
    trigger_id = body.trigger_id
    trigger_type = TriggerType.variation.value

    taskqueue.put(trigger_id, discord.variation, **body.dict())
    return {"trigger_id": trigger_id, "trigger_type": trigger_type}


async def reset(body: TriggerResetIn):
    trigger_id = body.trigger_id
    trigger_type = TriggerType.reset.value

    taskqueue.put(trigger_id, discord.reset, **body.dict())
    return {"trigger_id": trigger_id, "trigger_type": trigger_type}


async def describe(body: TriggerDescribeIn):
    trigger_id = body.trigger_id
    trigger_type = TriggerType.describe.value

    taskqueue.put(trigger_id, discord.describe, **body.dict())
    return {"trigger_id": trigger_id, "trigger_type": trigger_type}


async def upload_attachment(file: UploadFile):
    if not file.content_type.startswith("image/"):
        return {"message": "must image"}

    trigger_id = str(unique_id())
    filename = f"{trigger_id}.jpg"
    file_size = file.size
    attachment = await discord.upload_attachment(filename, file_size, await file.read())
    if not (attachment and attachment.get("upload_url")):
        return {"message": "Failed to upload image"}

    return {
        "upload_filename": attachment.get("upload_filename"),
        "upload_url": attachment.get("upload_url"),
        "trigger_id": trigger_id,
    }


async def send_message(body: SendMessageIn):
    picurl = await discord.send_attachment_message(body.upload_filename)
    if not picurl:
        return {"message": "Failed to send message"}

    return {"picurl": picurl}


async def queue_release(body: QueueReleaseIn):
    """bot 清除队列任务"""
    taskqueue.pop(body.trigger_id)

    return body


async def solo_variation(body: TriggerUVIn):
    trigger_id = body.trigger_id
    trigger_type = TriggerType.solo_variation.value
    taskqueue.put(trigger_id, discord.solo_variation, **body.dict())

    # 返回结果
    return {"trigger_id": trigger_id, "trigger_type": trigger_type}


async def solo_low_variation(body: TriggerUVIn):
    trigger_id = body.trigger_id
    trigger_type = TriggerType.solo_low_variation.value
    taskqueue.put(trigger_id, discord.solo_low_variation, **body.dict())

    # 返回结果
    return {"trigger_id": trigger_id, "trigger_type": trigger_type}


async def solo_high_variation(body: TriggerUVIn):
    trigger_id = body.trigger_id
    trigger_type = TriggerType.solo_high_variation.value
    taskqueue.put(trigger_id, discord.solo_high_variation, **body.dict())

    # 返回结果
    return {"trigger_id": trigger_id, "trigger_type": trigger_type}


async def expand(body: TriggerExpandIn):
    trigger_id = body.trigger_id
    trigger_type = TriggerType.expand.value
    taskqueue.put(trigger_id, discord.expand, **body.dict())

    # 返回结果
    return {"trigger_id": trigger_id, "trigger_type": trigger_type}


async def zoomout(body: TriggerZoomOutIn):
    trigger_id = body.trigger_id
    trigger_type = TriggerType.zoomout.value
    taskqueue.put(trigger_id, discord.zoomout, **body.dict())

    # 返回结果
    return {"trigger_id": trigger_id, "trigger_type": trigger_type}

