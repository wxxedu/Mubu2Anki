from aqt import mw
import os
import requests
import hashlib
import shutil
from aqt.utils import showInfo


def getMedia(url: str):
	fileAttribute = url.split(".")[-1]
	fileName = getHashValue(url) + "." + fileAttribute
	mediaFolderPath = mw.pm.profileFolder() + "/collection.media"
	if imageHasDownloaded(fileName, mediaFolderPath):
		return fileName
	else:
		r = requests.get(url, stream=True, timeout=5)
		if r.status_code == 200:
			r.raw.decode_content = True
			imagePath = mediaFolderPath + "/" + fileName
			with open(imagePath, "wb") as f:
				shutil.copyfileobj(r.raw, f)
			return fileName
		else:
			return url


def getHashValue(s: str) -> str:
	hashValue = hashlib.md5(s.encode())
	return str(hashValue.hexdigest())


def imageHasDownloaded(fileName: str, mediaFolderPath: str) -> bool:
	allFiles = os.listdir(mediaFolderPath)
	return allFiles.count(fileName) > 0

