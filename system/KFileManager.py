#!/usr/bin/python3
# -*- coding: utf-8 -*-

############################################
# Balabin kursovoy project 0.1
############################################
import sys
import os
import errno
import subprocess
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtGui import QKeySequence, QCursor, QDesktopServices
import shutil
import subprocess


class myWindow(QMainWindow):
    def __init__(self):
        super(myWindow, self).__init__()

        self.setStyleSheet(mystylesheet(self))
        self.setWindowTitle("Filemanager")
        self.setWindowIcon(QIcon.fromTheme("system- file-manager"))
        self.process = QProcess()

        self.settings = QSettings("QFileManager", "QFileManager")
        self.clip = QApplication.clipboard()
        self.isInEditMode = False

        self.treeview = QTreeView()
        self.listview = QTreeView()

        self.cut = False
        self.hiddenEnabled = False
        self.folder_copied = ""

        self.splitter = QSplitter()
        self.splitter.setOrientation(Qt.Horizontal)
        self.splitter.addWidget(self.treeview)
        self.splitter.addWidget(self.listview)

        hlay = QHBoxLayout()
        hlay.addWidget(self.splitter)

        wid = QWidget()
        wid.setLayout(hlay)
        self.createStatusBar()
        self.setCentralWidget(wid)
        self.setGeometry(0, 26, 900, 500)

        path = QDir.currentPath() #QDir.rootPath()
        path = self.parseRoot(path)
        self.root = path
        self.media = '/media'

        self.copyPath = ""
        self.copyList = []
        self.copyListNew = ""

        self.createActions()

        self.tBar = self.addToolBar("Tools")
        self.tBar.setContextMenuPolicy(Qt.PreventContextMenu)
        self.tBar.setMovable(False)
        self.tBar.setIconSize(QSize(16, 16))

        self.tBar.addSeparator()
        self.tBar.addAction(self.btnHome)
        self.tBar.addAction(self.btnDocuments)
        self.tBar.addAction(self.btnDownloads)
        self.tBar.addAction(self.btnMusic)
        self.tBar.addAction(self.btnPictures)
        self.tBar.addAction(self.btnVideo)
        self.tBar.addSeparator()
#        self.tBar.addAction(self.btnBack)
        self.tBar.addAction(self.btnUp)
        self.tBar.addSeparator()        
        self.tBar.addAction(self.btnProcesses)
        self.tBar.addAction(self.btnRemovables)
        self.tBar.addAction(self.btnQuests)
        self.tBar.addAction(self.btnTerminal)
        self.tBar.addSeparator()
        self.tBar.addAction(self.helpAction)

        self.dirModel = QFileSystemModel()
        self.dirModel.setReadOnly(False)
        self.dirModel.setFilter(QDir.NoDotAndDotDot | QDir.AllDirs | QDir.Drives)
        self.dirModel.setRootPath(QDir.rootPath())

        self.fileModel = QFileSystemModel()
        self.fileModel.setReadOnly(False)
        self.fileModel.setFilter(QDir.NoDotAndDotDot | QDir.AllDirs  | QDir.Files)
        self.fileModel.setResolveSymlinks(True)

        self.treeview.setModel(self.dirModel)
        self.treeview.hideColumn(1)
        self.treeview.hideColumn(2)
        self.treeview.hideColumn(3)

        self.listview.setModel(self.fileModel)
        self.treeview.setRootIsDecorated(True)

        self.listview.header().resizeSection(0, 320)
        self.listview.header().resizeSection(1, 80)
        self.listview.header().resizeSection(2, 80)
        self.listview.setSortingEnabled(True) 
        self.treeview.setSortingEnabled(True) 

        self.treeview.setRootIndex(self.dirModel.index(path))

        self.treeview.selectionModel().selectionChanged.connect(self.on_selectionChanged)
        self.listview.doubleClicked.connect(self.list_doubleClicked)

        self.treeview.setTreePosition(0)
        self.treeview.setUniformRowHeights(True)
        self.treeview.setExpandsOnDoubleClick(True)
        self.treeview.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.treeview.setIndentation(12)
        self.treeview.setDragDropMode(QAbstractItemView.DragDrop)
        self.treeview.setDragEnabled(True)
        self.treeview.setAcceptDrops(True)
        self.treeview.setDropIndicatorShown(True)
        self.treeview.sortByColumn(0, Qt.AscendingOrder)

        self.splitter.setSizes([20, 160])

        self.listview.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.listview.setDragDropMode(QAbstractItemView.DragDrop)
        self.listview.setDragEnabled(True)
        self.listview.setAcceptDrops(True)
        self.listview.setDropIndicatorShown(True)
        self.listview.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.listview.setIndentation(10)
        self.listview.sortByColumn(0, Qt.AscendingOrder)

        print("Welcome to FileManager")
        self.readSettings()
        self.enableHidden()
        self.getRowCount()
        self.treeview.setCurrentIndex(self.dirModel.index(self.root))


    def getRowCount(self):
        count = 0
        index = self.treeview.selectionModel().currentIndex()
        path = QDir(self.dirModel.fileInfo(index).absoluteFilePath())
        count = len(path.entryList(QDir.Files))
        self.statusBar().showMessage("%s %s" % (count, "Files"), 0)
        return count

    def closeEvent(self, e):
        print("writing settings ...\nGoodbye ...")
        self.writeSettings()

    def readSettings(self):
        print("reading settings ...")
        if self.settings.contains("pos"):
            pos = self.settings.value("pos", QPoint(200, 200))
            self.move(pos)
        else:
            self.move(0, 26)
        if self.settings.contains("size"):
            size = self.settings.value("size", QSize(800, 600))
            self.resize(size)
        else:
            self.resize(800, 600)
        if self.settings.contains("hiddenEnabled"):
            if self.settings.value("hiddenEnabled") == "false":
                self.hiddenEnabled = True
            else:
                self.hiddenEnabled = False

    def writeSettings(self):
        self.settings.setValue("pos", self.pos())
        self.settings.setValue("size", self.size())
        self.settings.setValue("hiddenEnabled", self.hiddenEnabled,)

    def enableHidden(self):
        if self.hiddenEnabled == False:
            self.fileModel.setFilter(QDir.NoDotAndDotDot | QDir.Hidden | QDir.AllDirs | QDir.Files)
            self.dirModel.setFilter(QDir.NoDotAndDotDot | QDir.Hidden | QDir.AllDirs)
            self.hiddenEnabled = True
            self.hiddenAction.setChecked(True)
            print("set hidden files to true")
        else:
            self.fileModel.setFilter(QDir.NoDotAndDotDot | QDir.AllDirs | QDir.Files)
            self.dirModel.setFilter(QDir.NoDotAndDotDot | QDir.AllDirs)
            self.hiddenEnabled = False
            self.hiddenAction.setChecked(False)
            print("set hidden files to false")

    def parseRoot(self, path):
        path = f'{path}'
        path = path[:path.rfind('/')]
        return path
        
    def aboutApp(self):
        import datetime
        import tkinter

        sysinfo = QSysInfo()
        myMachine = "currentCPU Architecture: " + sysinfo.currentCpuArchitecture() + "<br>" + sysinfo.prettyProductName()
        myMachine += "<br>" + sysinfo.kernelType() + " " + sysinfo.kernelVersion()
        title = "about QFileManager"
        message = """
                    <span style='color: #3465a4; font-size: 20pt;font-weight: bold;text-align: center;'
                    ></span></p><center><h3>Kursovoy FileManager<br>0.1a</h3></center>created by  
                    <a title='Balabin Valeriy' href='http://github.com' target='_blank'>Balabin Valeriy</a> with PyQt5<br><br>
                    <span style='color: white; font-size: 9pt;'>©2021 PSUTI<br><br></strong></span></p>
                        """ + myMachine
        
        root = tkinter.Tk()
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        tnow = datetime.datetime.now()
        message += f"""
            <br>
            11. current time : {tnow.hour}:{tnow.minute}
            <br>
            18. screen resolution: {screen_width} x {screen_height}
        """
        self.infosys(title, message)

    def infosys(self, title, message):
        QMessageBox(QMessageBox.Information, title, message, QMessageBox.NoButton, self, Qt.Dialog|Qt.NoDropShadowWindowHint | Qt.FramelessWindowHint).show()          

    ### actions
    def createActions(self):
        self.btnBack = QAction(QIcon.fromTheme("go-previous"), "go back", triggered = self.goBack)
        self.btnUp = QAction(QIcon.fromTheme("go-up"), "go up", triggered = self.goUp)
        self.btnHome = QAction(QIcon.fromTheme("go-home"), "home folder", triggered = self.goHome)
        self.btnMusic = QAction(QIcon.fromTheme("folder-music"), "music folder", triggered = self.goMusic)
        self.btnPictures = QAction(QIcon.fromTheme("folder-pictures"), "pictures folder", triggered = self.goPictures)
        self.btnDocuments = QAction(QIcon.fromTheme("folder-documents"), "documents folder", triggered = self.goDocuments)
        self.btnDownloads = QAction(QIcon.fromTheme("folder-downloads"), "downloads folder", triggered = self.goDownloads)
        self.btnVideo = QAction(QIcon.fromTheme("folder-videos"), "video folder", triggered = self.goVideo)
        self.btnProcesses = QAction(QIcon.fromTheme("system-search"), "processes", triggered = self.getProcessList)
        
        self.btnRemovables = QAction(QIcon.fromTheme("drive-removable-media"), 
            "removables", triggered = self.toggleRemovables)
        self.btnQuests = QAction(QIcon.fromTheme("applications-science"), "quests", triggered = self.showQuests)
        self.btnTerminal = QAction(QIcon.fromTheme("utilities-terminal"), "terminal", triggered = self.callTerminal)
        
        self.openAction = QAction(QIcon.fromTheme("system-run"), "open File",  triggered=self.openFile)
        self.openAction.setShortcut(QKeySequence(Qt.Key_Return))
        self.openAction.setShortcutVisibleInContextMenu(True)
        self.listview.addAction(self.openAction) 


        self.openActionText = QAction(QIcon.fromTheme("system-run"), "open File with built-in Texteditor",  triggered=self.openFileText)
        self.openActionText.setShortcut(QKeySequence(Qt.Key_F6))
        self.openActionText.setShortcutVisibleInContextMenu(True)
        self.listview.addAction(self.openActionText) 


        self.renameAction = QAction(QIcon.fromTheme("accessories-text-editor"), "rename File",  triggered=self.renameFile) 
        self.renameAction.setShortcut(QKeySequence(Qt.Key_F2))
        self.renameAction.setShortcutVisibleInContextMenu(True)
        self.listview.addAction(self.renameAction) 
        self.treeview.addAction(self.renameAction) 

        self.renameFolderAction = QAction(QIcon.fromTheme("accessories-text-editor"), "rename Folder",  triggered=self.renameFolder) 
        self.treeview.addAction(self.renameFolderAction) 

        self.copyAction = QAction(QIcon.fromTheme("edit-copy"), "copy File(s)",  triggered=self.copyFile) 
        self.copyAction.setShortcut(QKeySequence("Ctrl+c"))
        self.copyAction.setShortcutVisibleInContextMenu(True)
        self.listview.addAction(self.copyAction) 

        self.copyFolderAction = QAction(QIcon.fromTheme("edit-copy"), "copy Folder",  triggered=self.copyFolder) 
        self.treeview.addAction(self.copyFolderAction) 

        self.pasteFolderAction = QAction(QIcon.fromTheme("edit-paste"), "paste Folder",  triggered=self.pasteFolder) 
        self.treeview.addAction(self.pasteFolderAction) 

        self.cutAction = QAction(QIcon.fromTheme("edit-cut"), "cut File(s)",  triggered=self.cutFile) 
        self.cutAction.setShortcut(QKeySequence("Ctrl+x"))
        self.cutAction.setShortcutVisibleInContextMenu(True)
        self.listview.addAction(self.cutAction) 

        self.pasteAction = QAction(QIcon.fromTheme("edit-paste"), "paste File(s)",  triggered=self.pasteFile) 
        self.pasteAction.setShortcut(QKeySequence("Ctrl+v"))
        self.pasteAction.setShortcutVisibleInContextMenu(True)
        self.listview.addAction(self.pasteAction) 

        self.delAction = QAction(QIcon.fromTheme("edit-delete"), "delete File(s)",  triggered=self.deleteFile)
        self.delAction.setShortcut(QKeySequence("Shift+Del"))
        self.delAction.setShortcutVisibleInContextMenu(True)
        self.listview.addAction(self.delAction) 

        self.delFolderAction = QAction(QIcon.fromTheme("edit-delete"), "Delete Folder",  triggered=self.deleteFolder)
        self.delFolderAction.setShortcutVisibleInContextMenu(True)
        self.treeview.addAction(self.delFolderAction) 

        #
        self.moveToTrashAction = QAction(QIcon.fromTheme("user-trash"), "move to Trashbin",  triggered=self.moveToTrash)
        self.moveToTrashAction.setShortcut(QKeySequence("Del"))
        self.moveToTrashAction.setShortcutVisibleInContextMenu(True)        
        self.treeview.addAction(self.moveToTrashAction)         

        self.refreshAction = QAction(QIcon.fromTheme("view-refresh"), "refresh View",  triggered=self.refreshList, shortcut="F5")
        self.refreshAction.setShortcutVisibleInContextMenu(True)
        self.listview.addAction(self.refreshAction) 

        self.hiddenAction = QAction("show hidden Files",  triggered=self.enableHidden)
        self.hiddenAction.setShortcut(QKeySequence("Ctrl+h"))
        self.hiddenAction.setShortcutVisibleInContextMenu(True)
        self.hiddenAction.setCheckable(True)
        self.listview.addAction(self.hiddenAction)

        self.goBackAction = QAction(QIcon.fromTheme("go-back"), "go back",  triggered=self.goBack)
        self.goBackAction.setShortcut(QKeySequence(Qt.Key_Backspace))
        self.goBackAction.setShortcutVisibleInContextMenu(True)
        self.listview.addAction(self.goBackAction) 

        self.helpAction = QAction(QIcon.fromTheme("help"), "About",  triggered=self.aboutApp)
        self.helpAction.setShortcut(QKeySequence(Qt.Key_F1))
        self.helpAction.setShortcutVisibleInContextMenu(True)
        self.listview.addAction(self.helpAction) 

        self.createFolderAction = QAction(QIcon.fromTheme("folder-new"), "create new Folder",  triggered=self.createNewFolder)
        self.createFolderAction.setShortcut(QKeySequence("Shift+Ctrl+n"))
        self.createFolderAction.setShortcutVisibleInContextMenu(True)
        self.treeview.addAction(self.createFolderAction) 


    def checkIsApplication(self, path):
        st = subprocess.check_output("file  --mime-type '" + path + "'", stderr=subprocess.STDOUT, universal_newlines=True, shell=True)
        print(st)
        if "application/x-executable" in st:
            print(path, "is an application")
            return True
        else:
            return False

    def refreshList(self):
        print("refreshing view")
        index = self.listview.selectionModel().currentIndex()
        path = self.fileModel.fileInfo(index).path()
        self.treeview.setCurrentIndex(self.fileModel.index(path))
        self.treeview.setFocus()


    def on_selectionChanged(self):
        self.treeview.selectionModel().clearSelection()
        index = self.treeview.selectionModel().currentIndex()
        path = self.dirModel.fileInfo(index).absoluteFilePath()
        self.listview.setRootIndex(self.fileModel.setRootPath(path))
        self.currentPath = path
        self.setWindowTitle(path)
        self.getRowCount()

    def openFile(self):
        if self.listview.hasFocus():
            index = self.listview.selectionModel().currentIndex()
            path = self.fileModel.fileInfo(index).absoluteFilePath()
            self.copyFile()
            for files in self.copyList:
                print("%s '%s'" % ("open file", files))
                if self.checkIsApplication(path) == True:
                    self.process.startDetached(files)
                else:
                    QDesktopServices.openUrl(QUrl(files , QUrl.TolerantMode | QUrl.EncodeUnicode))

    def openFileText(self):
        if self.listview.selectionModel().hasSelection():
            index = self.listview.selectionModel().currentIndex()
            path = self.fileModel.fileInfo(index).absoluteFilePath()
            subprocess.Popen(["code", path], stdin=open(os.devnull, 'r'))


    def list_doubleClicked(self):
        index = self.listview.selectionModel().currentIndex()
        path = self.fileModel.fileInfo(index).absoluteFilePath()

        if not self.fileModel.fileInfo(index).isDir():
            if self.checkIsApplication(path) == True:
                self.process.startDetached(path)
            else:
                QDesktopServices.openUrl(QUrl(path , QUrl.TolerantMode | QUrl.EncodeUnicode))
        else:
            self.treeview.setCurrentIndex(self.dirModel.index(path))
            self.treeview.setFocus()
            self.setWindowTitle(path)

    def goBack(self):
        index = self.listview.selectionModel().currentIndex()
        path = self.fileModel.fileInfo(index).path()
        self.treeview.setCurrentIndex(self.dirModel.index(path))

    def goUp(self):
        index = self.treeview.selectionModel().currentIndex()
        path = self.dirModel.fileInfo(index).path()

        if path.find(self.root) >= 0:
            self.treeview.setCurrentIndex(self.dirModel.index(path))
        else:
            self.treeview.setCurrentIndex(self.dirModel.index(self.root))

    def goHome(self):
        docs = self.root + "/home"
        # docs = QStandardPaths.standardLocations(QStandardPaths.HomeLocation)[0]
        self.treeview.setCurrentIndex(self.dirModel.index(docs))
        self.treeview.setFocus()

    def goMusic(self):
        docs = self.root + "/home/music"
        # docs = QStandardPaths.standardLocations(QStandardPaths.MusicLocation)[0]
        self.treeview.setCurrentIndex(self.dirModel.index(docs))
        self.treeview.setFocus()

    def goPictures(self):
        docs = self.root + "/home/pictures"
        # docs = QStandardPaths.standardLocations(QStandardPaths.PicturesLocation)[0]
        self.treeview.setCurrentIndex(self.dirModel.index(docs))
        self.treeview.setFocus()        

    def goVideo(self):
        docs = self.root + "/home/videos"
        # docs = QStandardPaths.standardLocations(QStandardPaths.MoviesLocation)[0]
        self.treeview.setCurrentIndex(self.dirModel.index(docs))
        self.treeview.setFocus()

    def goDocuments(self):
        docs = self.root + "/home/documents"
        # docs = QStandardPaths.standardLocations(QStandardPaths.DocumentsLocation)[0]
        self.treeview.setCurrentIndex(self.dirModel.index(docs))
        self.treeview.setFocus()

    def goDownloads(self):
        docs = self.root + "/home/downloads"
        # docs = QStandardPaths.standardLocations(QStandardPaths.DownloadLocation)[0]
        self.treeview.setCurrentIndex(self.dirModel.index(docs))
        self.treeview.setFocus()

    def getProcessList(self):
        import procform
        self.processes = QWidget()
        ui = procform.ProcWindow(self.processes)
        self.processes.show()


    def toggleRemovables(self):
        self.root, self.media = self.media, self.root
        self.treeview.setRootIndex(self.dirModel.index(self.root))        
        self.treeview.setCurrentIndex(self.dirModel.index(self.root))
        

    def showQuests(self):
        try:
            subprocess.run(['partitionmanager'])
        except:
            try:
                subprocess.run(['gnome-disks'])
            except:
                print('disk-utility not opened')
        

    def callTerminal(self):
        try:
            subprocess.run(['gnome-terminal'])
        except:
            try:
                subprocess.run(['konsole'])
            except:
                print('terminal not opened')

    def infobox(self, message):
        title = "QFilemager"
        QMessageBox(QMessageBox.Information, title, message, QMessageBox.NoButton, self, Qt.Dialog|Qt.NoDropShadowWindowHint).show()  

    def systemPathCheck(self, path):
        if path.find(self.root + "/system") >=0 :
            return True
        else:
            return False

    def contextMenuEvent(self, event):
        index = self.listview.selectionModel().currentIndex()
        path = self.fileModel.fileInfo(index).absoluteFilePath()
        self.menu = QMenu(self.listview)
        if self.listview.hasFocus():
            self.menu.addAction(self.createFolderAction)
            self.menu.addAction(self.openAction)
            self.menu.addAction(self.openActionText)
            self.menu.addAction(self.renameAction) 

            self.menu.addSeparator()
            self.menu.addAction(self.copyAction) 
            self.menu.addAction(self.cutAction) 
            self.menu.addAction(self.pasteAction) 
            self.menu.addAction(self.moveToTrashAction)
            self.menu.addAction(self.delAction)

            self.menu.addSeparator()
            self.menu.addAction(self.helpAction) 
            self.menu.popup(QCursor.pos())
        else:
            index = self.treeview.selectionModel().currentIndex()
            path = self.dirModel.fileInfo(index).absoluteFilePath()
            print("current path is:", path)
            self.menu = QMenu(self.treeview)
            if os.path.isdir(path):
                self.menu.addAction(self.createFolderAction)
                self.menu.addAction(self.renameFolderAction)
                self.menu.addAction(self.copyFolderAction)
                self.menu.addAction(self.pasteFolderAction)
                self.menu.addAction(self.delFolderAction)
            self.menu.popup(QCursor.pos())

    def createNewFolder(self):
        index = self.treeview.selectionModel().currentIndex()
        path = self.dirModel.fileInfo(index).absoluteFilePath()
        dlg = QInputDialog(self)
        foldername, ok = dlg.getText(self, 'Folder Name', "Folder Name:", QLineEdit.Normal, "", Qt.Dialog)
        if ok:
            success = QDir(path).mkdir(foldername)

    def renameFile(self):
        if self.listview.hasFocus():
            if self.listview.selectionModel().hasSelection():
                index = self.listview.selectionModel().currentIndex()
                path = self.fileModel.fileInfo(index).absoluteFilePath() 
                basepath = self.fileModel.fileInfo(index).path() 
                print(basepath)

                if self.systemPathCheck(basepath):
                    self.infobox("System folder protected from editing")
                    return

                oldName = self.fileModel.fileInfo(index).fileName() 
                dlg = QInputDialog()
                newName, ok = dlg.getText(self, 'new Name:', path, QLineEdit.Normal, oldName, Qt.Dialog)
                if ok:
                    newpath = basepath + "/" + newName
                    QFile.rename(path, newpath)
        elif self.treeview.hasFocus():
            self.renameFolder()

    def renameFolder(self):
        index = self.treeview.selectionModel().currentIndex()
        path = self.dirModel.fileInfo(index).absoluteFilePath()
        basepath = self.dirModel.fileInfo(index).path() 
        print("basepath:", basepath)

        if self.systemPathCheck(basepath):
            self.infobox("System folder protected from editing")
            return

        oldName = self.dirModel.fileInfo(index).fileName() 
        dlg = QInputDialog()
        newName, ok = dlg.getText(self, 'new Name:', path, QLineEdit.Normal, oldName, Qt.Dialog)
        if ok:
            newpath = basepath + "/" + newName
            print(newpath)
            nd = QDir(path)
            check = nd.rename(path, newpath)

    def copyFile(self):
        self.copyList = []
        selected = self.listview.selectionModel().selectedRows()
        count = len(selected)
        for index in selected:
            path = self.currentPath + "/" + self.fileModel.data(index,self.fileModel.FileNameRole)
            print(path, "copied to clipboard")
            self.copyList.append(path)
            self.clip.setText('\n'.join(self.copyList))
        print("%s\n%s" % ("filepath(s) copied:", '\n'.join(self.copyList)))

    def copyFolder(self):
        index = self.treeview.selectionModel().currentIndex()
        folderpath = self.dirModel.fileInfo(index).absoluteFilePath()  
        print("%s\n%s" % ("folderpath copied:", folderpath))
        self.folder_copied = folderpath
        self.copyList = []

    def pasteFolder(self):
        index = self.treeview.selectionModel().currentIndex()
        target = self.folder_copied
        destination = self.dirModel.fileInfo(index).absoluteFilePath() + "/" + QFileInfo(self.folder_copied).fileName()
        print("%s %s %s" % (target, "will be pasted to", destination))

        if self.systemPathCheck(destination):
            self.infobox("System folder protected from editing")
            return

        try:
            shutil.copytree(target, destination)
        except OSError as e:
            if e.errno == errno.ENOTDIR:
                shutil.copy(target, destination)
            else:
                self.infobox('Error', 'Directory not copied. Error: %s' % e)

    def pasteFile(self):
        if len(self.copyList) > 0:
            index = self.treeview.selectionModel().currentIndex()
            file_index = self.listview.selectionModel().currentIndex()
            for target in self.copyList:
                print(target)
                destination = self.dirModel.fileInfo(index).absoluteFilePath() + "/" + QFileInfo(target).fileName()
                print("%s %s" % ("pasted File to", destination))

                if self.systemPathCheck(destination):
                    self.infobox("System folder protected from editing")
                    return

                QFile.copy(target, destination)
                if self.cut == True:
                    QFile.remove(target)
                self.cut == False
        else:
            index = self.treeview.selectionModel().currentIndex()
            target = self.folder_copied
            destination = self.dirModel.fileInfo(index).absoluteFilePath() + "/" + QFileInfo(self.folder_copied).fileName()

            if self.systemPathCheck(destination):
                self.infobox("System folder protected from editing")
                return

            try:
                shutil.copytree(target, destination)
            except OSError as e:
                
                # If the error was caused because the source wasn't a directory
                if e.errno == errno.ENOTDIR:
                    shutil.copy(target, destination)
                else:
                    print('Directory not copied. Error: %s' % e)

    def cutFile(self):
        self.cut = True
        self.copyFile()

    def deleteFolder(self):
        index = self.treeview.selectionModel().currentIndex()
        delFolder  = self.dirModel.fileInfo(index).absoluteFilePath()
        msg = QMessageBox.question(self, "Info", "Caution!\nReally delete this Folder?\n" + delFolder, QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        if msg == QMessageBox.Yes:
            print('Deletion confirmed.')

            if self.systemPathCheck(delFolder):
                self.infobox("System folder protected from editing")
                return

            self.statusBar().showMessage("%s %s" % ("folder deleted", delFolder), 0)
            self.fileModel.remove(index)
            print("%s %s" % ("folder deleted", delFolder))
        else:
            print('No clicked.')

    def moveToTrash(self):
        def pasteToTrash(self):
            if len(self.copyList) > 0:
                index = self.root + "/trashbin"
                for target in self.copyList:
                    print(target)
                    destination = index + "/" + QFileInfo(target).fileName()
                    print("%s %s" % ("pasted File to", destination))
                    QFile.copy(target, destination)
                    try:
                        shutil.copytree(target, destination)
                    except OSError as e:
                        pass
            else:
                print('No files have been selected')

        self.copyFile()


        msg = QMessageBox.question(self, "Info", 
            "Caution!\nReally move this Files to Trashbin?\n" + '\n'.join(self.copyList), 
                QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)

        if msg == QMessageBox.Yes:
            print('Removing confirmed.')
            pasteToTrash(self)
            index = self.listview.selectionModel().currentIndex()
            self.copyPath = self.fileModel.fileInfo(index).absoluteFilePath()

            if self.systemPathCheck(self.copyPath):
                self.infobox("System folder protected from editing")
                return

            print("%s %s" % ("file removed", self.copyPath))
            self.statusBar().showMessage("%s %s" % ("file removed", self.copyPath), 0)
            for delFile in self.listview.selectionModel().selectedIndexes():
                self.fileModel.remove(delFile)
        else:
            print('No clicked.')

    def deleteFile(self):
        self.copyFile()
        msg = QMessageBox.question(self, "Info", 
            "Caution!\nReally delete this Files?\n" + '\n'.join(self.copyList), 
                QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)

        if msg == QMessageBox.Yes:
            print('Deletion confirmed.')
            index = self.listview.selectionModel().currentIndex()
            self.copyPath = self.fileModel.fileInfo(index).absoluteFilePath()

            if self.systemPathCheck(self.copyPath):
                self.infobox("System folder protected from editing")
                return

            print("%s %s" % ("file deleted", self.copyPath))
            self.statusBar().showMessage("%s %s" % ("file deleted", self.copyPath), 0)
            for delFile in self.listview.selectionModel().selectedIndexes():
                self.fileModel.remove(delFile)
        else:
            print('No clicked.')

    def createStatusBar(self):
        sysinfo = QSysInfo()
        myMachine = "current CPU Architecture: " + sysinfo.currentCpuArchitecture() + " *** " + sysinfo.prettyProductName() + " *** " + sysinfo.kernelType() + " " + sysinfo.kernelVersion()
        self.statusBar().showMessage(myMachine, 0)

def mystylesheet(self):
    return """
QTreeView
{
background: #1a1a1a;
background: transparent;
selection-color: black;
border: 1px solid lightgrey;
selection-background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #729fcf, stop: 1  #204a87);
color: white;
outline: 0;
} 

}
QTreeView::item::focus
{
background: transparent;
background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #729fcf, stop: 1  #204a87);
border: 0px;
}
QMenu
{
color: white;
background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                 stop: 0 #E1E1E1, stop: 0.4 #DDDDDD,
                                 stop: 0.5 #D8D8D8, stop: 1.0 #D3D3D3);
background: #2d3033;                                 
}
QMenu::item::selected
{
color: black;
background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 gray, stop: 1  darkgray);
border: 0px;
}
QHeaderView
{
background: #d3d7cf;
color: #555753;
font-weight: bold;
}
QStatusBar
{
font-size: 8pt;
color: #555753;
}
QMenuBar
{
background: transparent;
color: gray;
border: 0px;
}
QToolBar
{
background: transparent;
background: black
border: 0px;
}
QMainWindow
{
     background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                 stop: 0 #E1E1E1, stop: 0.4 #DDDDDD,
                                 stop: 0.5 #D8D8D8, stop: 1.0 #D3D3D3);
}
QLabel
{
    font-size: 10pt;
    text-align: center;
     background: transparent;
    color:gray;
}
QMessageBox
{
    font-size: 10pt;
    text-align: center;
     background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                 stop: 0 #E1E1E1, stop: 0.4 #DDDDDD,
                                 stop: 0.5 #D8D8D8, stop: 1.0 #D3D3D3);
    color: white;
    background: transparent;
}
QPushButton{
background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 white, stop: 1 grey);
border-style: solid;
border-color: darkgrey;
height: 26px;
width: 66px;
font-size: 8pt;
border-width: 1px;
border-radius: 6px;
}
QPushButton:hover:!pressed{
background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 lightblue, stop: 1  blue);
border-style: solid;
border-color: darkgrey;
height: 26px;
width: 66px;
border-width: 1px;
border-radius: 6px;
}
QPushButton:hover{
background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 lightgreen, stop: 1  green);
border-style: solid;
border-color: darkgrey;
border-width: 1px;
border-radius: 4px;
}
QToolButton
{
padding-left: 2px; padding-right: 2px;
}
    """       

if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = myWindow()
    w.show()
    if len(sys.argv) > 1:
        path = sys.argv[1]
        print(path)
        w.listview.setRootIndex(w.fileModel.setRootPath(path))
        w.treeview.setRootIndex(w.dirModel.setRootPath(path))
        w.setWindowTitle(path)
    sys.exit(app.exec_())
    
