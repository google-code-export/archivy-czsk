# -*- coding: UTF-8 -*-
from skin import parseColor

from Screens.Screen import Screen
from Screens.VirtualKeyBoard import VirtualKeyBoard
from Components.ConfigList import ConfigList, ConfigListScreen
from Components.config import config, configfile
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.ProgressBar import ProgressBar
from Components.FileList import FileList
from Components.Sources.StaticText import StaticText

from Plugins.Extensions.archivCZSK import _
import Plugins.Extensions.archivCZSK.settings as settings
import Plugins.Extensions.archivCZSK.resources.archives.config as archives_config

from base import BaseArchivCZSKScreen
from info import ChangelogScreen



class CategoryWidget():
    color_black = "#000000"
    color_white = "#ffffff"
    color_red = "#ff0000"
    color_grey = "#5c5b5b"
    
    def __init__(self, screen, name, label):
        print 'intializing category widget %s-%s' % (name, label.encode('utf-8'))
        self.screen = screen
        self.name = name
        self.label = label
        self.x_position = 0
        self.y_position = 0
        self.x_size = 100
        self.y_size = 100
        self.active = False

        self.foregroundColor_inactive = self.color_white
        self.backgroundColor_inactive = self.color_black
        self.foregroundColor_active = self.color_red
        self.backgroundColor_active = self.color_black
        
        self.screen[self.name] = Label(label.encode('utf-8'))
        
    def get_skin_string(self):
        return """<widget name="%s" size="%d,%d" position="%d,%d" zPosition="1" backgroundColor="%s" foregroundColor="%s" font="Regular;20"  halign="center" valign="center" />"""\
             % (self.name, self.x_size, self.y_size, self.x_position, self.y_position, self.backgroundColor_inactive, self.foregroundColor_inactive)
    
    def setText(self, text):
        self.screen[self.name].setText(text)
        
    def activate(self):
        self.active = True
        self.setText(self.label.encode('utf-8'))
        self.screen[self.name].instance.setForegroundColor(parseColor(self.foregroundColor_active))
        self.screen[self.name].instance.setBackgroundColor(parseColor(self.backgroundColor_active))
        
    def deactivate(self):
        self.active = False
        self.setText(self.label.encode('utf-8'))
        self.screen[self.name].instance.setForegroundColor(parseColor(self.foregroundColor_inactive))
        self.screen[self.name].instance.setBackgroundColor(parseColor(self.backgroundColor_inactive))
        
        
class CategoryWidgetHD(CategoryWidget):
    def __init__(self, screen, name, label, x_position, y_position):
        CategoryWidget.__init__(self, screen, name, label)
        self.x_position = x_position
        self.y_position = y_position
        self.x_size = 130
        self.y_size = 30
        
class CategoryWidgetSD(CategoryWidget):
    def __init__(self, screen, name, label, x_position, y_position):
        CategoryWidget.__init__(self, screen, name, label)
        self.x_position = x_position
        self.y_position = y_position
        self.x_size = 80
        self.y_size = 30
    
class BaseArchivCZSKConfigScreen(BaseArchivCZSKScreen, ConfigListScreen):

    def __init__(self, session, categories=[]):
        BaseArchivCZSKScreen.__init__(self, session)
        ConfigListScreen.__init__(self, [], session=session, on_change=self.changedEntry)
        self.onChangedEntry = [ ]
        
        self.categories = categories
        self.selected_category = 0
        self.config_list_entries = []
        self.category_widgets = []
        
        self.initializeCategories()
        self.initializeSkin()
        
        self["key_yellow"] = Label(_("changelog"))
        self["key_green"] = Label(_("Save"))
        self["key_red"] = Label(_("Cancel"))
        self["key_blue"] = Label(_("Next"))
        
        self["actions"] = ActionMap(["SetupActions", "ColorActions"],
            {
                "cancel": self.keyCancel,
                "green": self.keySave,
                "ok": self.keyOk,
                "red": self.keyCancel,
                "blue": self.nextCategory,
                "yellow": self.changelog
            }, -2)
        
    def initializeSkin(self):
        if self.HD:
            self.skin = """
            <screen position="335,140" size="610,435" >
                <widget name="key_red" position="10,5" zPosition="1" size="140,45" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" shadowOffset="-2,-2" shadowColor="black" />
                <widget name="key_green" position="160,5" zPosition="1" size="140,45" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" shadowOffset="-2,-2" shadowColor="black" />
                <widget name="key_yellow" position="310,5" zPosition="1" size="140,45" font="Regular;20" halign="center" valign="center" backgroundColor="#a08500" shadowOffset="-2,-2" shadowColor="black" />
                <widget name="key_blue" position="460,5" zPosition="1" size="140,45" font="Regular;20" halign="center" valign="center" backgroundColor="#18188b" shadowOffset="-2,-2" shadowColor="black" />
                <eLabel position="-1,55" size="612,1" backgroundColor="#999999" />"""   
            self.skin += '\n' + self.getCategoriesWidgetString()
                
            self.skin += """<widget name="config" position="0,100" size="610,300" scrollbarMode="showOnDemand" />
                        </screen>"""
        else:
            self.skin = """
            <screen position="335,140" size="610,435" >
                <widget name="key_red" position="10,5" zPosition="1" size="140,45" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" shadowOffset="-2,-2" shadowColor="black" />
                <widget name="key_green" position="160,5" zPosition="1" size="140,45" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" shadowOffset="-2,-2" shadowColor="black" />
                <widget name="key_yellow" position="310,5" zPosition="1" size="140,45" font="Regular;20" halign="center" valign="center" backgroundColor="#a08500" shadowOffset="-2,-2" shadowColor="black" />
                <widget name="key_blue" position="460,5" zPosition="1" size="140,45" font="Regular;20" halign="center" valign="center" backgroundColor="#18188b" shadowOffset="-2,-2" shadowColor="black" />
                <eLabel position="-1,55" size="612,1" backgroundColor="#999999" />"""   
            self.skin += '\n' + self.getCategoriesWidgetString()
                
            self.skin += """<widget name="config" position="0,100" size="610,300" scrollbarMode="showOnDemand" />
                        </screen>"""
                        
        #print "initialized skin %s" % self.skin
                        
     
    def initializeCategories(self):
        self.createCategoryWidgets() 
     
                                 
    def createCategoryWidget(self, name, label, x_position, y_position):
        if self.HD:
            return CategoryWidgetHD(self, name, label, x_position, y_position)
        else:
            return CategoryWidgetSD(self, name, label, x_position, y_position)
    
    def createCategoryWidgets(self):
        space = 5
        x_position = 5
        y_position = 60
        for idx, category in enumerate(self.categories):
            cat_widget = self.createCategoryWidget('category' + str(idx), category['label'], x_position, y_position)
            self.category_widgets.append(cat_widget)
            x_position += cat_widget.x_size + space
            

    def getCategoriesWidgetString(self):
        return '\n'.join(cat_widget.get_skin_string() for cat_widget in self.category_widgets)
    
    def nextCategory(self):
        if len(self.categories) > 0:
            self.changeCategory()     
            
    def refreshConfigList(self):
        if len(self.categories) > 0:  
            config_list = self.categories[self.selected_category]['subentries']
            if hasattr(config_list, '__call__'):
                config_list = config_list()
            
            self.config_list_entries = config_list
        
        self.category_widgets[self.selected_category].activate()
        self["config"].list = self.config_list_entries
        self["config"].setList(self.config_list_entries)
        
           
     
    def changeCategory(self):
        current_category = self.selected_category
        if self.selected_category == len(self.categories) - 1:
            self.selected_category = 0
        else:
            self.selected_category += 1
            
        config_list = self.categories[self.selected_category]['subentries']
        
        # for dynamic menus we can use functions to retrieve config list
        if hasattr(config_list, '__call__'):
            config_list = config_list()
            
        self.config_list_entries = config_list
        
        self.category_widgets[current_category].deactivate()
        self.category_widgets[self.selected_category].activate()
        
        self["config"].list = self.config_list_entries
        self["config"].setList(self.config_list_entries)
        
            
    def changelog(self):
        pass     
    
    def KeyOk(self):
        pass
    
    def KeyCancel(self):
        pass
        
    def changedEntry(self):
        for x in self.onChangedEntry:
            x()
        
    def keySave(self):
        self.saveAll()
        self.close(True)

    def keyCancel(self):
        for x in self["config"].list:
            x[1].cancel()
        self.close()
        
    def keyLeft(self):
        ConfigListScreen.keyLeft(self) 

    def keyRight(self):
        ConfigListScreen.keyRight(self)



class ArchiveCZSKConfigScreen(BaseArchivCZSKConfigScreen): 
    def __init__(self, session):
        
        categories = [
                      {'label':_("Main"), 'subentries':settings.get_main_settings},
                      {'label':_("Player"), 'subentries':settings.get_player_settings},
                      {'label':_("Path"), 'subentries':settings.get_path_settings}
                     ]
        
        BaseArchivCZSKConfigScreen.__init__(self, session, categories=categories)
        self.onLayoutFinish.append(self.layoutFinished)
        self.onShown.append(self.buildMenu)

    def layoutFinished(self):
        self.setTitle(_("Configuration of ArchivCZSK"))
        
    
    def buildMenu(self):
        self.refreshConfigList()
    
    def keyOk(self):
        current = self["config"].getCurrent()[1]
        if current == config.plugins.archivCZSK.subtitlesPath:
            self.session.openWithCallback(self.pathSelectedSubtitles, SelectPath, config.plugins.archivCZSK.subtitlesPath.value)
        if current == config.plugins.archivCZSK.dataPath:
            self.session.openWithCallback(self.pathSelectedData, SelectPath, config.plugins.archivCZSK.dataPath.value)
        if current == config.plugins.archivCZSK.downloadsPath:
            self.session.openWithCallback(self.pathSelectedDownloads, SelectPath, config.plugins.archivCZSK.downloadsPath.value)
        pass
    
    def pathSelectedSubtitles(self, res):
        if res is not None:
            config.plugins.archivCZSK.subtitlesPath.value = res
    
    def pathSelectedData(self, res):
        if res is not None:
            config.plugins.archivCZSK.dataPath.value = res
    
    def pathSelectedDownloads(self, res):
        if res is not None:
            config.plugins.archivCZSK.downloadsPath.value = res

    def keyLeft(self):
        ConfigListScreen.keyLeft(self) 
        if self["config"].getCurrent()[1] == config.plugins.archivCZSK.player:
            self.buildMenu()

    def keyRight(self):
        ConfigListScreen.keyRight(self)
        if self["config"].getCurrent()[1] == config.plugins.archivCZSK.player:
            self.buildMenu()
          
        
 
class ArchiveConfigScreen(BaseArchivCZSKConfigScreen):
    def __init__(self, session, archive):
        self.session = session
        self.archive = archive
        self.setup_title = _("Settings of ") + archive.name.encode('utf-8')
        categories = archives_config.getArchiveConfigList(self.archive)
        
        BaseArchivCZSKConfigScreen.__init__(self, session, categories=categories)
        
        
        self.onShown.append(self.buildMenu)
        self.onLayoutFinish.append(self.layoutFinished)

    def layoutFinished(self):
        self.setTitle(_("Settings of") + ' ' + self.archive.name.encode('utf-8'))
            
    
    def changelog(self):
        self.session.open(ChangelogScreen, self.archive)
        
    def buildMenu(self):
        self.refreshConfigList() 
        
    def keyOk(self):
        current = self["config"].getCurrent()[1]
        if current == config.plugins.archivCZSK.archives.voyo.password:
            self.session.openWithCallback(lambda x : self.VirtualKeyBoardCallback(x, 'password'), VirtualKeyBoard, title=(_("Enter the password:")), text=config.plugins.archivCZSK.archives.voyo.password.value)
        elif current == config.plugins.archivCZSK.archives.stream.username:
            self.session.openWithCallback(lambda x : self.VirtualKeyBoardCallback(x, 'username'), VirtualKeyBoard, title=(_("Enter the username:")), text=config.plugins.archivCZSK.archives.stream.username.value)        
        else:
            pass          
            
    def VirtualKeyBoardCallback(self, callback=None, entry=None):
        if callback is not None and len(callback) and entry is not None and len(entry):
            if entry == 'password':
                config.plugins.archivCZSK.archives.voyo.password.setValue(callback)
            if entry == 'username':
                config.plugins.archivCZSK.archives.stream.username.setValue(callback)



class SelectPath(Screen):
    skin = """<screen name="SelectPath" position="center,center" size="560,320">
            <ePixmap pixmap="skin_default/buttons/red.png" position="0,0" zPosition="0" size="140,40" transparent="1" alphatest="on" />
            <ePixmap pixmap="skin_default/buttons/green.png" position="140,0" zPosition="0" size="140,40" transparent="1" alphatest="on" />
            <ePixmap pixmap="skin_default/buttons/yellow.png" position="280,0" zPosition="0" size="140,40" transparent="1" alphatest="on" />
            <ePixmap pixmap="skin_default/buttons/blue.png" position="420,0" zPosition="0" size="140,40" transparent="1" alphatest="on" />
            <widget name="target" position="0,60" size="540,22" valign="center" font="Regular;22" />
            <widget name="filelist" position="0,100" zPosition="1" size="560,220" scrollbarMode="showOnDemand"/>
            <widget render="Label" source="key_red" position="0,0" size="140,40" zPosition="5" valign="center" halign="center" backgroundColor="red" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />
            <widget render="Label" source="key_green" position="140,0" size="140,40" zPosition="5" valign="center" halign="center" backgroundColor="red" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />
        </screen>"""
    def __init__(self, session, initDir):
        Screen.__init__(self, session)
        inhibitDirs = ["/bin", "/boot", "/dev", "/etc", "/lib", "/proc", "/sbin", "/sys", "/usr", "/var"]
        inhibitMounts = []
        self["filelist"] = FileList(initDir, showDirectories=True, showFiles=False, inhibitMounts=inhibitMounts, inhibitDirs=inhibitDirs)
        self["target"] = Label()
        self["actions"] = ActionMap(["WizardActions", "DirectionActions", "ColorActions", "EPGSelectActions"],
        {
            "back": self.cancel,
            "left": self.left,
            "right": self.right,
            "up": self.up,
            "down": self.down,
            "ok": self.ok,
            "green": self.green,
            "red": self.cancel
            
        }, -1)
        self["key_red"] = StaticText(_("Cancel"))
        self["key_green"] = StaticText(_("OK"))
        self.onShown.append(self.setWindowTitle)
        
    def setWindowTitle(self):
        self.setTitle(_("Select directory"))

    def cancel(self):
        self.close(None)

    def green(self):
        self.close(self["filelist"].getSelection()[0])

    def up(self):
        self["filelist"].up()
        self.updateTarget()

    def down(self):
        self["filelist"].down()
        self.updateTarget()

    def left(self):
        self["filelist"].pageUp()
        self.updateTarget()

    def right(self):
        self["filelist"].pageDown()
        self.updateTarget()

    def ok(self):
        if self["filelist"].canDescent():
            self["filelist"].descent()
            self.updateTarget()

    def updateTarget(self):
        currFolder = self["filelist"].getSelection()[0]
        if currFolder is not None:
            self["target"].setText(currFolder)
        else:
            self["target"].setText(_("Invalid Location"))

