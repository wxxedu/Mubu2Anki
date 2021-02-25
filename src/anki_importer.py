import re
import hashlib
from aqt.utils import showInfo
from aqt import *
from anki.notes import Note


italic2Cloze = False
underline2Cloze = True


def importToAnki(notes: list, fileName: str) -> list:
	deckName = fileName + "$h1$$h2$$h3$$h4$"
	headingsCount = [0, 0, 0]
	metadata = "$1$$2$$3$$4$$5$$6$$7$$8$$9$$10$$11$$12$$13$$14$$15$$16$$17$$18$$19$$20$"
	for note in notes:
		if note["hl"] != -1:
			headingAttributeString = ""
			headingsCount[note["hl"] - 1] += 1
			for i in range(note["hl"] + 1, 4):
				headingAttributeString = headingAttributeString + "$h%d$" % i
				headingsCount[i - 1] = 0
			deckName = deckName.split("$h%d$" % note["hl"])[0] + "$h%d$" % note["hl"] + "%003d - " % headingsCount[note["hl"] - 1] + getPlainText(note["mc"]) + headingAttributeString
		realDeckName = re.sub(r"\$h\d\$", "::", deckName)
		realDeckName = realDeckName.rstrip(":")
		indentAttributeString = ""
		for i in range(note["il"] + 1, 21):
			indentAttributeString = indentAttributeString + "$%d$" % i
		metadata = metadata.split("$%d$" % note["il"])[0] + "$%d$" % note["il"] + mathConversion(getPlainText(note["mc"])) + indentAttributeString
		realMetadata = re.sub(r"\$\d+\$", " → ", metadata)
		realMetadata = realMetadata.rstrip(" → ").lstrip(" → ")
		realMetadata = realMetadata.rsplit(" → " + mathConversion(getPlainText(note["mc"])), 1)[0]
		mainNoteBasicAdder(note, realDeckName, realMetadata)


def getPlainText(htext: str) -> str:
	htext = re.sub(r"<([^>]*?)>", "", htext)
	htext = re.sub(r"(?!\{\{c(?:\d+|¡)::)(.*?)(?!\}\})", r"\1", htext)
	return htext


def mathConversion(htext: str) -> str:
	return re.sub(r"\\\[(.*?)\\\]", r"\(\1\)", htext)


def mainNoteBasicAdder(cardDict: dict, fileName: str, metadata: str):
	mainContent: str = cardDict["mc"]
	noteContent: str = cardDict["nc"]
	mainContent = mainContent.lstrip(" ").rstrip(" ")
	noteContent = noteContent.lstrip(" ").rstrip(" ")
	tags = cardDict["tg"]
	hasCloze = False
	if underline2Cloze:
		clozeNum = 0
		if re.search(r"<u>(?!{{c(?:\d+)::)(.*?)(?!}})</u>", mainContent):
			hasCloze = True
			while re.search(r"<u>(?!{{c(?:\d+)::)(.*?)(?!}})</u>", mainContent):
				clozeNum = clozeNum + 1
				mainContent = re.sub(r"<u>(?!{{c(?:\d+)::)(.*?)(?!}})</u>", r"<u>{{c%d::\1}}</u>" % clozeNum, mainContent, 1)
	if hasCloze:
		add2Anki(fileName, "Mubu Cloze", [mainContent, noteContent, tags, metadata])
	elif noteContent != "":
		add2Anki(fileName, "Mubu Basic", [mainContent, noteContent, tags, metadata])


def add2Anki(deckName: str, cardType: str, contentList: list) -> list:
	deckId = mw.col.decks.id(deckName)
	mw.col.decks.select(deckId)
	cardModel = mw.col.models.byName(cardType)
	if cardModel:
		deck = mw.col.decks.get(deckId)
		deck["mid"] = cardModel["id"]
		mw.col.decks.save(deck)
		note = mw.col.newNote(deckId)
		frontText: str = contentList[0]
		backText: str = contentList[1]
		metadata: str = contentList[3]
		frontPlainText: str = getPlainText(frontText)
		hashValue = hashlib.md5(frontPlainText.encode())
		hashForQuery = str(hashValue.hexdigest())
		note["Front"] = frontText
		note["Back"] = backText
		note["QueryHash"] = hashForQuery
		note["Metadata"] = metadata
		for tag in contentList[2]:
			note.addTag(tag)
		dupeOrEmpty = note.dupeOrEmpty()
		if dupeOrEmpty == 2:
			dupeIDs = mw.col.find_notes(hashForQuery)
			for dupeID in dupeIDs:
				oldNote = mw.col.getNote(dupeID)
				if oldNote["Front"] == note["Front"] and oldNote["Back"] == note["Back"] and oldNote["Metadata"] == note["Metadata"]:
					pass
				else:
					keepOldOrNewWindow = KeepOldOrNew(aqt.mw, oldNote, note, deckId)
					keepOldOrNewWindow.exec_()
		else:
			mw.col.add_note(note, deckId)
	else:
		showInfo(
			"You have not installed the anki templates. Please download them from <a href = \"\">the GitHub Page</a> for this addon and install them.")


class KeepOldOrNew(QDialog):
	def __init__(self, mw, oldNote: Note, newNote: Note, deckID):
		super().__init__(mw)
		grid = QGridLayout(self)
		grid.setSpacing(10)
		self.noteFromFile = QTextEdit(self)
		self.noteFromFile.setReadOnly(True)
		self.noteFromAnki = QTextEdit(self)
		self.noteFromAnki.setReadOnly(True)
		self.keepOld = QPushButton("Keep Old")
		self.keepOld.setShortcut("1")
		self.keepNew = QPushButton("Keep New")
		self.keepNew.setShortcut("2")
		self.keepNew.setDefault(True)
		grid.addWidget(QLabel("Old Note"), 0, 0)
		grid.addWidget(QLabel("New Note"), 0, 1)
		grid.addWidget(self.noteFromFile, 1, 1)
		grid.addWidget(self.noteFromAnki, 1, 0)
		grid.addWidget(self.keepNew, 2, 1)
		grid.addWidget(self.keepOld, 2, 0)
		self.keepNew.clicked.connect(self.keepNewNote)
		self.keepOld.clicked.connect(self.keepOldNote)
		self.oldNote = oldNote
		self.newNote = newNote
		self.deckID = deckID
		self.noteFromFile.setHtml(newNote["Front"] + "<br><label style = \"font-size: 10px; font-style: italics; color: gray\">" + newNote["Metadata"] + "</label><hr>" + newNote["Back"])
		self.noteFromAnki.setHtml(oldNote["Front"] + "<br><label style = \"font-size: 10px; font-style: italics; color: gray\">" + oldNote["Metadata"] + "</label><hr>" + oldNote["Back"])
		self.noteFromFile.update()
		self.noteFromAnki.update()
		self.show()

	def keepOldNote(self):
		aqt.mw.col.set_deck(self.oldNote.card_ids(), self.deckID)
		self.oldNote.flush()
		self.close()

	def keepNewNote(self):
		aqt.mw.col.add_note(self.newNote, self.deckID)
		aqt.mw.col.remove_notes([self.oldNote.id])
		self.close()
