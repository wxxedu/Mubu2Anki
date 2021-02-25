import aqt
import os
import re
from aqt.qt import *
from aqt.utils import showInfo
from .opmlProcessor import processOpml
from .anki_importer import importToAnki
from aqt import mw


class FileSelector(QDialog):
	def __init__(self, mw):
		super().__init__(mw)
		path = os.path.expanduser("~/Downloads")
		allFiles = os.listdir(path)
		for singleFile in allFiles:
			if singleFile.endswith(".opml"):
				try:
					os.rename(path + "/%s" % singleFile, path + "/OPML Files/%s" % singleFile)
				except FileNotFoundError:
					os.mkdir(path + "/OPML Files")
					os.rename(path + "/%s" % singleFile, path + "/OPML Files/%s" % singleFile)
		fileDirectory = QFileDialog.getOpenFileName(self, "Choose Your OPML Files", path + "/OPML Files", "OPML(*.opml)")
		mainProcess(fileDirectory)
		delete_empty_decks()
		aqt.mw.update()
		aqt.mw.reset(True)


def mainProcess(fileDirectory: str) -> list:
	path = os.path.expanduser("~/Downloads")
	try:
		with open(fileDirectory[0], encoding="utf-8") as file:
			fileContent = file.read()
			fileContent = fileContent.replace("\n", "<br>")
			fileContent = re.search(r"<body>(.*)</body>", fileContent).group(1)
			fileContentLines = fileContent.split("<br>    ")
			fileName = re.search(r"(?:.*)/(.+?)(-\d)?\.opml", fileDirectory[0]).group(1)
			fileName = fileName.replace("+", " ")
			try:
				os.rename(fileDirectory[0], path + "/OPML Files/Processed Files/" + fileName + ".opml")
			except FileNotFoundError:
				os.mkdir(path + "/OPML Files/Processed Files")
				os.rename(fileDirectory[0], path + "/OPML Files/Processed Files/" + fileName + ".opml")
			return importToAnki(processOpml(fileContentLines), fileName)
	except FileNotFoundError:
		return None


def delete_empty_decks():
	names_and_ids = mw.col.decks.all_names_and_ids()
	for name_and_id in names_and_ids:
		# I could not find what type this object is, so the only way for me to do it now is to use the string.
		name_and_id_segments = str(name_and_id).split("\n")
		deck_id= int(name_and_id_segments[0].split(": ")[1])
		if deck_has_cards(deck_id):
			mw.col.decks.rem(deck_id, True, True)


def deck_has_cards(deck_id):
	if deck_id != 1:
		try:
			if mw.col.decks.card_count(deck_id, True) == 0:
				return True
		except AttributeError:
			cids = mw.col.decks.cids(deck_id, True)
			if len(cids) == 0:
				return True
	return False


action = QAction("Choose Your File", aqt.mw)
action.setShortcut("Ctrl+M")
action.triggered.connect(lambda: FileSelector(aqt.mw))
aqt.mw.form.menuTools.addAction(action)
