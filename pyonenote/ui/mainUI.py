#!/usr/bin/env python


#############################################################################
##
## Copyright (C) 2014 Riverbank Computing Limited.
## Copyright (C) 2010 Nokia Corporation and/or its subsidiary(-ies).
## All rights reserved.
##
## This file is part of the examples of PyQt.
##
## $QT_BEGIN_LICENSE:BSD$
## You may use this file under the terms of the BSD license as follows:
##
## "Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are
## met:
##   * Redistributions of source code must retain the above copyright
##     notice, this list of conditions and the following disclaimer.
##   * Redistributions in binary form must reproduce the above copyright
##     notice, this list of conditions and the following disclaimer in
##     the documentation and/or other materials provided with the
##     distribution.
##   * Neither the name of Nokia Corporation and its Subsidiary(-ies) nor
##     the names of its contributors may be used to endorse or promote
##     products derived from this software without specific prior written
##     permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
## "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
## LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
## A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
## OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
## SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
## LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
## DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
## THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
## (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
## OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
## $QT_END_LICENSE$
##
#############################################################################
from PyQt5.QtCore import (QFile, QFileInfo, QPoint, QSettings, QSize,
                          Qt, QTextStream, QMetaObject, pyqtSlot, QVariant)
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtWebKitWidgets import QWebView
from PyQt5.QtWidgets import (QAction, QApplication, QFileDialog, QMainWindow,
                             QMessageBox, QTextEdit, QStyleFactory, QGroupBox, QHBoxLayout, QListWidget,
                             QListWidgetItem, QLabel,
                             QTreeWidget, QTreeWidgetItem, QVBoxLayout)

from pyonenote.api.pages import FetchPage
from pyonenote.database.database_manager import Dbm, SyncAllThread


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.dbm_obj = Dbm()
        self.curFile = ''
        self.textEdit = QTextEdit()
        self.sectionTreeWidget = QTreeWidget()

        self.notesListWidget = QListWidget()
        self.createHorizontalGroupBox()
        self.setCentralWidget(self.horizontalGroupBox)

        self.createActions()
        self.createMenus()
        self.createToolBars()
        self.createStatusBar()
        self.readSettings()

        [self.hierarchy_dict, self.notebook_dict, self.section_dict, self.page_dict] = [{}, {}, {}, {}]

        self.setCurrentFile('')

        # For binding slots and signals
        self.fetchPageThread = FetchPage()
        self.fetchPageThread.setObjectName('fetchPageThread')
        self.syncAllThread = SyncAllThread()
        self.syncAllThread.setObjectName('syncAllThread')
        self.textEdit.document().contentsChanged.connect(self.documentWasModified)
        self.sectionTreeWidget.setObjectName("sectionTreeWidget")
        self.notesListWidget.setObjectName("notesListWidget")
        QMetaObject.connectSlotsByName(self)

    @pyqtSlot()
    def on_sectionTreeWidget_itemSelectionChanged(self):
        for x in self.sectionTreeWidget.selectedItems():
            if x.text(1) in self.section_dict.keys():
                self.populate_notes_list(x.parent().text(1), x.text(1))

    @pyqtSlot()
    def on_notesListWidget_itemSelectionChanged(self):
        for x in self.notesListWidget.selectedItems():
            self.fetchPageThread.fetchSignal.connect(self.on_fetchPageThread_fetchComplete)
            self.titleLabel.setText("Syncing")
            self.statusBar().showMessage("Syncing")
            # self.fetchPageThread.fetchSignal.connect(lambda:self.view.setHtml("<body>hello world</body>"))
            self.fetchPageThread.fetch(self.page_dict[x.data(1)])

    def on_fetchPageThread_fetchComplete(self, string):
        self.view.setHtml(string)
        self.titleLabel.setText(self.view.title())
        self.statusBar().showMessage("Page fetched")

    def on_syncAllThread_syncComplete(self, dbm):
        self.dbm_obj = dbm
        self.statusBar().showMessage("Sync complete")

    def createHorizontalGroupBox(self):
        self.horizontalGroupBox = QGroupBox()
        layout = QHBoxLayout()

        self.sectionTreeWidget.setHeaderHidden(1)
        layout.addWidget(self.sectionTreeWidget, 0)
        self.notesListWidget.setWindowTitle('Notes')
        layout.addWidget(self.notesListWidget, 0)

        subVBox = QGroupBox()
        vLayout = QVBoxLayout()

        self.titleLabel = QLabel()
        vLayout.addWidget(self.titleLabel, 0)

        self.view = QWebView()
        vLayout.addWidget(self.view, 1)

        subVBox.setLayout(vLayout)

        layout.addWidget(subVBox, 1)

        self.horizontalGroupBox.setLayout(layout)

    def closeEvent(self, event):
        if self.maybeSave():
            self.writeSettings()
            event.accept()
        else:
            event.ignore()

    def newFile(self):
        self.readDB()
        # if self.maybeSave():
        #     self.textEdit.clear()
        #     self.setCurrentFile('')

    def open(self):
        if self.maybeSave():
            fileName, _ = QFileDialog.getOpenFileName(self)
            if fileName:
                self.loadFile(fileName)

    def save(self):
        if self.curFile:
            return self.saveFile(self.curFile)

        return self.saveAs()

    def saveAs(self):
        fileName, _ = QFileDialog.getSaveFileName(self)
        if fileName:
            return self.saveFile(fileName)
        return False

    def on_sectionList_selection_changed(self):
        print('selected item index changed '),

    def populate_section_list(self, hierarchy, notebook_dict, section_dict):
        for notebook_id in hierarchy.keys():
            notebook_sectionTreeWidget = QTreeWidgetItem(self.sectionTreeWidget,
                                                         [notebook_dict[notebook_id].name, notebook_id])
            for section_id in hierarchy[notebook_id].keys():
                QTreeWidgetItem(notebook_sectionTreeWidget, [section_dict[section_id].name, section_id])
        self.sectionTreeWidget.show()

    def populate_notes_list(self, notebook_id, section_id):
        self.notesListWidget.clear()
        for page_id in self.hierarchy_dict[notebook_id][section_id]:
            item = QListWidgetItem(self.page_dict[page_id].title, self.notesListWidget)
            item.setData(1, QVariant(page_id))

    def readDB(self):

        self.dbm_obj.read()
        [self.hierarchy_dict, self.notebook_dict, self.section_dict, self.page_dict] = self.dbm_obj.get_hierarchy_dict()
        self.populate_section_list(self.hierarchy_dict, self.notebook_dict, self.section_dict)

    def sync(self):
        self.syncAllThread.syncCompleteSignal.connect(self.on_syncAllThread_syncComplete)
        self.statusBar().showMessage("Syncing")
        self.syncAllThread.sync(self.dbm_obj)

    def about(self):
        QMessageBox.about(self, "About Application",
                          "The <b>Application</b> example demonstrates how to write "
                          "modern GUI applications using Qt, with a menu bar, "
                          "toolbars, and a status bar.")

    def documentWasModified(self):
        self.setWindowModified(self.textEdit.document().isModified())

    def createActions(self):
        root = QFileInfo(__file__).absolutePath()

        self.newAct = QAction(QIcon(root + '/images/new.png'), "&New", self,
                              shortcut=QKeySequence.New, statusTip="Create a new file",
                              triggered=self.newFile)

        self.openAct = QAction(QIcon(root + '/images/open.png'), "&Open...",
                               self, shortcut=QKeySequence.Open,
                               statusTip="Open an existing file", triggered=self.open)

        self.saveAct = QAction(QIcon(root + '/images/save.png'), "&Save", self,
                               shortcut=QKeySequence.Save,
                               statusTip="Save the document to disk", triggered=self.save)

        self.saveAsAct = QAction("Save &As...", self,
                                 shortcut=QKeySequence.SaveAs,
                                 statusTip="Save the document under a new name",
                                 triggered=self.saveAs)

        self.syncAct = QAction("S&ync", self,
                               statusTip="Sync everything",
                               triggered=self.sync)

        self.readDBAct = QAction("Read DB", self, statusTip="Read stored DB",
                                 triggered=self.readDB)

        self.exitAct = QAction("E&xit", self, shortcut="Ctrl+Q",
                               statusTip="Exit the application", triggered=self.close)

        self.cutAct = QAction(QIcon(root + '/images/cut.png'), "Cu&t", self,
                              shortcut=QKeySequence.Cut,
                              statusTip="Cut the current selection's contents to the clipboard",
                              triggered=self.textEdit.cut)

        self.copyAct = QAction(QIcon(root + '/images/copy.png'), "&Copy", self,
                               shortcut=QKeySequence.Copy,
                               statusTip="Copy the current selection's contents to the clipboard",
                               triggered=self.textEdit.copy)

        self.pasteAct = QAction(QIcon(root + '/images/paste.png'), "&Paste",
                                self, shortcut=QKeySequence.Paste,
                                statusTip="Paste the clipboard's contents into the current selection",
                                triggered=self.textEdit.paste)

        self.aboutAct = QAction("&About", self,
                                statusTip="Show the application's About box",
                                triggered=self.about)

        self.aboutQtAct = QAction("About &Qt", self,
                                  statusTip="Show the Qt library's About box",
                                  triggered=QApplication.instance().aboutQt)

        self.cutAct.setEnabled(False)
        self.copyAct.setEnabled(False)
        self.textEdit.copyAvailable.connect(self.cutAct.setEnabled)
        self.textEdit.copyAvailable.connect(self.copyAct.setEnabled)

    def createMenus(self):
        self.fileMenu = self.menuBar().addMenu("&File")
        self.fileMenu.addAction(self.newAct)
        self.fileMenu.addAction(self.openAct)
        self.fileMenu.addAction(self.saveAct)
        self.fileMenu.addAction(self.saveAsAct)
        self.fileMenu.addAction(self.syncAct)
        self.fileMenu.addAction(self.readDBAct)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.exitAct)

        self.editMenu = self.menuBar().addMenu("&Edit")
        self.editMenu.addAction(self.cutAct)
        self.editMenu.addAction(self.copyAct)
        self.editMenu.addAction(self.pasteAct)

        self.menuBar().addSeparator()

        self.helpMenu = self.menuBar().addMenu("&Help")
        self.helpMenu.addAction(self.aboutAct)
        self.helpMenu.addAction(self.aboutQtAct)

    def createToolBars(self):
        self.fileToolBar = self.addToolBar("File")
        self.fileToolBar.addAction(self.newAct)
        self.fileToolBar.addAction(self.openAct)
        self.fileToolBar.addAction(self.saveAct)

        self.editToolBar = self.addToolBar("Edit")
        self.editToolBar.addAction(self.cutAct)
        self.editToolBar.addAction(self.copyAct)
        self.editToolBar.addAction(self.pasteAct)

    def createStatusBar(self):
        self.statusBar().showMessage("Ready")

    def readSettings(self):
        settings = QSettings("Trolltech", "Application Example")
        pos = settings.value("pos", QPoint(200, 200))
        size = settings.value("size", QSize(400, 400))
        self.resize(size)
        self.move(pos)

    def writeSettings(self):
        settings = QSettings("Trolltech", "Application Example")
        settings.setValue("pos", self.pos())
        settings.setValue("size", self.size())

    def maybeSave(self):
        if self.textEdit.document().isModified():
            ret = QMessageBox.warning(self, "Application",
                                      "The document has been modified.\nDo you want to save "
                                      "your changes?",
                                      QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)

            if ret == QMessageBox.Save:
                return self.save()

            if ret == QMessageBox.Cancel:
                return False

        return True

    def loadFile(self, fileName):
        file = QFile(fileName)
        if not file.open(QFile.ReadOnly | QFile.Text):
            QMessageBox.warning(self, "Application",
                                "Cannot read file %s:\n%s." % (fileName, file.errorString()))
            return

        inf = QTextStream(file)
        QApplication.setOverrideCursor(Qt.WaitCursor)
        self.textEdit.setPlainText(inf.readAll())
        QApplication.restoreOverrideCursor()

        self.setCurrentFile(fileName)
        self.statusBar().showMessage("File loaded", 2000)

    def saveFile(self, fileName):
        file = QFile(fileName)
        if not file.open(QFile.WriteOnly | QFile.Text):
            QMessageBox.warning(self, "Application",
                                "Cannot write file %s:\n%s." % (fileName, file.errorString()))
            return False

        outf = QTextStream(file)
        QApplication.setOverrideCursor(Qt.WaitCursor)
        outf << self.textEdit.toPlainText()
        QApplication.restoreOverrideCursor()

        self.setCurrentFile(fileName);
        self.statusBar().showMessage("File saved", 2000)
        return True

    def setCurrentFile(self, fileName):
        self.curFile = fileName
        self.textEdit.document().setModified(False)
        self.setWindowModified(False)

        if self.curFile:
            shownName = self.strippedName(self.curFile)
        else:
            shownName = 'untitled.txt'

        self.setWindowTitle("%s[*] - Application" % shownName)

    def strippedName(self, fullFileName):
        return QFileInfo(fullFileName).fileName()

    def write_at_exit(self):
        self.dbm_obj.write([self.hierarchy_dict, self.notebook_dict, self.section_dict, self.page_dict])

if __name__ == '__main__':
    import sys
    import atexit

    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create('Fusion'))
    mainWin = MainWindow()
    atexit.register(mainWin.write_at_exit)
    mainWin.show()
    sys.exit(app.exec_())
